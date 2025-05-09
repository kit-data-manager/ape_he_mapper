#Mapping service is reachable before starting with plugin
GET {{host}}
HTTP 200

GET {{host}}/api/v1/mappingAdministration/types
HTTP 200
[Captures]
mappingType: jsonpath "$[0].id"

#---------------- BEGIN Test Mapping for Ape-He ----------------------------------

# Register a dummy mapping
POST {{host}}/api/v1/mappingAdministration/
Content-Type: multipart/form-data; boundary=boundary
[Options]
variable: id1=0
--boundary
Content-Disposition: form-data; name="record"; filename="record.json"
Content-Type: application/json

< ./record.json
--boundary
Content-Disposition: form-data; name="document"; filename="document.json"
Content-Type: application/json

< ./document.json
--boundary--

HTTP 201

# Execute mapping
POST {{host}}/api/v1/mappingExecution/{{id1}}
[MultipartFormData]
document: file,./tests/sampleData/XMCD.nxs;
HTTP 200
[Captures]
result1: body
[Asserts]
body contains "entry"

# Get plugin ETag
GET {{host}}/api/v1/mappingAdministration/{{id1}}
HTTP 200
[Captures]
etag: header "ETag"

# Delete plugin
DELETE {{host}}/api/v1/mappingAdministration/{{id1}}
If-Match: {{etag}}
HTTP 204

#---------------- END Test Mapping for Ape-He ----------------------------------
