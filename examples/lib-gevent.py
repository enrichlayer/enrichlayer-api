import csv

from enrichlayer_client.gevent import EnrichLayer, do_bulk

enrichlayer = EnrichLayer()

balance = enrichlayer.get_balance()

print("Balance:", balance)

person = enrichlayer.person.get(
    linkedin_profile_url="https://sg.linkedin.com/in/williamhgates"
)
print("Person Result:", person)

company = enrichlayer.company.get(url="https://www.linkedin.com/company/apple")
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
results = do_bulk(bulk_linkedin_person_data)

print("Bulk:", results)
