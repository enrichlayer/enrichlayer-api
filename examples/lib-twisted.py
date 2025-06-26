import csv

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from enrichlayer_client.twisted import EnrichLayer, do_bulk

enrichlayer = EnrichLayer()


@inlineCallbacks
def main():
    balance = yield enrichlayer.get_balance()
    print("Balance:", balance)

    person = yield enrichlayer.person.get(
        linkedin_profile_url="https://sg.linkedin.com/in/williamhgates"
    )

    print("Person:", person)

    company = yield enrichlayer.company.get(
        url="https://www.linkedin.com/company/apple"
    )

    print("Company:", company)

    # PROCESS BULK WITH CSV
    bulk_linkedin_person_data = []
    with open("sample.csv") as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            bulk_linkedin_person_data.append(
                (enrichlayer.person.get, {"linkedin_profile_url": row[0]})
            )
    bulk = yield do_bulk(bulk_linkedin_person_data)

    print("Bulk:", bulk)

    reactor.stop()


main()

reactor.run()
