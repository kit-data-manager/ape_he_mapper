#Mapping service is reachable before starting with plugin
GET {host}
HTTP 200

GET {host}/api/v1/mappingAdministration/types
HTTP 200
[Captures]
mappingType: jsonpath "$[0].id"

#---------------- BEGIN Test Mapping for Ape-He ----------------------------------

# Register a dummy mapping
[Options]
variable: id1=apeHe-{{mappingType}}-20250507T114106Z

POST {host}/api/v1/mappingAdministration/
Content-Type: multipart/form-data; boundary=boundary
```
--boundary
Content-Disposition: form-data; name="record"; filename="record.json"
Content-Type: application/json

{"mappingId":"{{id1}}","mappingType":"{{mappingType}}","title":"apeHe from CI test","description":"","acl":[]}
--boundary
Content-Disposition: form-data; name="document"; filename="document.json"
Content-Type: application/json

{"PrivateFei.TimeOfCreation":"entry.endTime"}
--boundary--
```
HTTP 201

# Execute mapping with Thermofisher sample
POST {host}/api/v1/mappingExecution/{id1}
[MultipartFormData]
document: file,./tests/sampleData/XMCD.nxs;
HTTP 200
[Captures]
result1: body
[Asserts]
body contains "entry"

#---------------- END Test Mapping for Ape-He ----------------------------------
