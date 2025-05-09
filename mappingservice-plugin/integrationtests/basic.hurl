# Check if the mapping service is reachable
GET {{host}}
HTTP 200

# Get mapping types
GET {{host}}/api/v1/mappingAdministration/types
HTTP 200
[Captures]
mappingType: jsonpath "$[0].id"

# ---------------- BEGIN Test Mapping for Ape-He ----------------

# Register a dummy mapping with separate JSON files
POST {{host}}/api/v1/mappingAdministration/
[Options]
variable: id1=0
[MultipartFormData]
record: file,record.json; type=application/json
document: file,document.json; type=application/json
HTTP 201

# Execute mapping with test data
POST {{host}}/api/v1/mappingExecution/{{id1}}
[MultipartFormData]
document: file,./tests/sampleData/XMCD.nxs;
HTTP 200
[Captures]
result1: body
[Asserts]
body contains "entry"

# Get the ETag of the registered mapping
GET {{host}}/api/v1/mappingAdministration/{{id1}}
HTTP 200
[Captures]
etag: header "ETag"

# Delete the registered mapping
DELETE {{host}}/api/v1/mappingAdministration/{{id1}}
If-Match: {{etag}}
HTTP 204

# ---------------- END Test Mapping for Ape-He ----------------
