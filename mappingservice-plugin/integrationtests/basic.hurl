#Mapping service is reachable before starting with plugin
GET {{host}}
HTTP 200

GET {{host}}/api/v1/mappingAdministration/types
HTTP 200
[Captures]
mappingType: jsonpath "$[0].id"

#---------------- BEGIN Test Mapping for Ape-He ----------------------------------

#Register with a very small portion of real mapping file info as dummy mapping file
POST {{host}}/api/v1/mappingAdministration/
Content-Type: multipart/form-data; boundary=boundary
[Options] #set all variables you need for further use in this hurl script
variable: id1=0
```
--boundary
Content-Disposition: form-data; name="record"; filename="blob"
Content-Type: application/json

{"mappingId":"{{id1}}","mappingType": "{{mappingType}}","title":"apeHe from CI test","description":"","acl":[]}
--boundary
Content-Disposition: form-data; name="document"; filename="blob"
Content-Type: application/json

{"PrivateFei.TimeOfCreation":"entry.endTime"}
```
HTTP 201

#Execute Mapping with APE-HE sample
POST {{host}}/api/v1/mappingExecution/{{id1}}
[MultipartFormData]
document: file,./tests/sampleData/XMCD.nxs;
HTTP 200
[Captures]
result1: body
[Asserts]
body contains "entry"

#---------------- END Test Mapping for Ape-He ----------------------------------