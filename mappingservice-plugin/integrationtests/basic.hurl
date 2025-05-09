# ----------------------------------------------------------
# Check if the mapping service is reachable
#-----------------------------------------------------------
GET {{host}}
HTTP 200

# ----------------------------------------------------------
# Get mapping types from the mapping service 
# to fetch the first available id
# ----------------------------------------------------------
GET {{host}}/api/v1/mappingAdministration/types
HTTP 200
[Captures]
mappingType: jsonpath "$[0].id"

# ---------------- BEGIN Test Mapping for Ape-He -----------

# ----------------------------------------------------------
# Register a dummy mapping with created files:
# - record.json (containing the mapping scheme metadata)
# - document.json (containing the dummy map file)
# ----------------------------------------------------------
POST {{host}}/api/v1/mappingAdministration/
[Options]
variable: id1=96
[MultipartFormData]
record: file,record.json; type=application/json
document: file,document.json; type=application/json
HTTP 201  # Expect plugin to be successfully created

# ----------------------------------------------------------
# Execute mapping with test data
# ----------------------------------------------------------
POST {{host}}/api/v1/mappingExecution/{{id1}}
[MultipartFormData]
document: file,./tests/sampleData/XMCD.nxs;
HTTP 200
[Captures]
result1: body
[Asserts]
body contains "entry"  # Expect some result structure containing "entry"

# ----------------------------------------------------------
# Get the ETag of the registered mapping
# ----------------------------------------------------------
GET {{host}}/api/v1/mappingAdministration/{{id1}}
HTTP 200
[Captures]
etag: header "ETag"  # Capture Etag used for delete

# -----------------------------------------------------------
# Delete the registered mapping
# -----------------------------------------------------------
DELETE {{host}}/api/v1/mappingAdministration/{{id1}}
If-Match: {{etag}}
HTTP 204  # Expect a successful deletion

# ---------------- END Test Mapping for Ape-He ----------------
