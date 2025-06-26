import asyncio
import csv

from enrichlayer_client.asyncio import EnrichLayer, do_bulk

enrichlayer = EnrichLayer()


balance = asyncio.run(enrichlayer.get_balance())

print("Balance:", balance)

person = asyncio.run(
    enrichlayer.person.get(
        linkedin_profile_url="https://sg.linkedin.com/in/williamhgates"
    )
)

print("Person Result:", person)

company = asyncio.run(
    enrichlayer.company.get(url="https://www.linkedin.com/company/apple")
)

print("Company Result:", company)

# PROCESS BULK WITH CSV
bulk_linkedin_person_data = []
with open("sample.csv") as file:
    reader = csv.reader(file)
    next(reader, None)
    for row in reader:
        bulk_linkedin_person_data.append(
            (enrichlayer.person.get, {"linkedin_profile_url": row[0]})
        )
results = asyncio.run(do_bulk(bulk_linkedin_person_data))

print("Bulk:", results)
