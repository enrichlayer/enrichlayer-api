import asyncio
from asyncio.queues import QueueEmpty
from dataclasses import dataclass
import json
import logging
from typing import Any, Callable, Generic, TypeVar, Union

import aiohttp

from enrichlayer_client.config import MAX_WORKERS

logger = logging.getLogger(__name__)

T = TypeVar("T")
Op = tuple[Callable, dict]


@dataclass
class Result(Generic[T]):
    success: bool
    value: T
    error: BaseException


class EnrichLayerException(Exception):
    """Raised when InternalServerError or network error or request error"""

    pass


class EnrichLayerBase:
    api_key: str
    base_url: str
    timeout: int
    max_retries: int
    max_backoff_seconds: int

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int,
        max_retries: int,
        max_backoff_seconds: int,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_backoff_seconds = max_backoff_seconds

    async def request(
        self,
        method: str,
        url: str,
        result_class: type[T],
        params: dict = None,
        data: dict = None,
    ) -> Union[T, dict]:
        if params is None:
            params = {}
        if data is None:
            data = {}
        api_endpoint = f"{self.base_url}{url}"
        header_dic = {"Authorization": "Bearer " + self.api_key}
        backoff_in_seconds = 1
        for i in range(0, self.max_retries):
            try:
                if method.lower() == "get":
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            api_endpoint,
                            params=params,
                            headers=header_dic,
                            timeout=self.timeout,
                        ) as response:
                            response_result = await response.read()
                            status = response.status
                elif method.lower() == "post":
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            api_endpoint,
                            json=data,
                            headers=header_dic,
                            timeout=self.timeout,
                        ) as response:
                            response_result = await response.read()
                            status = response.status
                if status in [200, 202]:
                    response_json = json.loads(response_result)
                    try:
                        return result_class(**response_json)
                    except Exception:
                        return response_json
                else:
                    raise EnrichLayerException(response_result.decode("utf-8"))

            except EnrichLayerException as e:
                if status in [400, 401, 403, 404]:
                    logger.exception(str(e))
                    raise e

                if status == 500:
                    if i < 1:
                        continue
                    else:
                        raise e

                if status == 429:
                    sleep = backoff_in_seconds * 2**i
                    await asyncio.sleep(min(self.max_backoff_seconds, sleep))

                if i < self.max_retries:
                    continue
                else:
                    raise e

        # If we reach here, all retries failed
        raise EnrichLayerException("Max retries exceeded")


async def do_bulk(ops: list[Op], max_workers: int = MAX_WORKERS) -> list[Result]:
    """Bulk operation

    This function can be used to run bulk operations using a limited number of concurrent requests.

    :param ops: List of operation function and parameter
    :type ops: List[Tuple[Callable, Dict]]
    :param max_workers: Total concurrent request, defaults to 10
    :type max_workers: int
    :return: Once all operation is finished this function will return List[:class:`proxycurl.asyncio.base.Result`]
    :rtype: List[:class:`proxycurl.asyncio.base.Result`]

    """

    results: list[Result[Any]] = [None for _ in range(len(ops))]  # type: ignore

    queue: asyncio.Queue = asyncio.Queue()

    for job in enumerate(ops):
        await queue.put(job)

    workers = []

    for _ in range(max_workers):
        workers.append(_worker(queue, results))

    await asyncio.gather(*workers)

    return results


async def _worker(queue, results):
    while True:
        try:
            index, op = queue.get_nowait()
        except QueueEmpty:
            break

        try:
            response = await op[0](**op[1])
            results[index] = Result(True, response, None)
        except Exception as e:
            results[index] = Result(False, None, e)
        queue.task_done()
