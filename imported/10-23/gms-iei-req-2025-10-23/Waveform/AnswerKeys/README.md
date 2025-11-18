The GMS SME Team developed these request and response answer keys for waveform domain requests from the DAL.

# Waveform Domain Answer Key Descriptions
POC: Nicole McMahon, SNL, nmcmaho@sandia.gov<br>
Updated: 28-Jul-2025

#### File Name Stucture 
Skeleton: {endpoint}/{time_format}/{endpoint}\_{test \#}_[request,response]\_{time_format}.{file extension}

- **{time_format}** corresponds to requests/responses in ISO-8601 format or epoch TIMESTAMP format
- **{endpoint}** corresponds to the "Domain Priority" number in the endpoint priority spreadsheet
- **{test \#}** corresponds to a test case number
- **{request}** corresponds to some sort of input needed to create the response
- **{response}** corresonds to some sort of output generated from the request

Examples: 
- **wa-1_test1_request.txt** - request body for test #1 of the WA-1 endpoint; contains a comment and the text for the dataselect POST request
- **wa-1_test1_response.json** - respose body for test #1 of the WA-1 endpoint in JSON format

## WA-1 - /dataselect/1/query
Retrieves the raw waveforms by cahnnels and time range

#### Request Bodies
Text files containing the POST body submitted to the dataselect service.

#### Response Bodies
JSON files containin the expect response from the dataselect service for given inputs.

#### Tests
1. Return 10 minutes of E1-format waveform data
2. Return waveform data from multiple channels
3. Return waveform data from two different .w files (across a day boundary)
4. Return waveform data for the same channel requested multiple times
5. Return empty if a non-existent channel is requested
6. Return waveforms read from different channels in the same .w file

## WA-2 - /waveform/qcsegment/query/channels-timerange
Retrieves QC Segments by channels and time range

#### Request Bodies
JSON files capturing the requests to the DAL

#### Response Bodies
JSON files containin the expect response from the DAL

#### Tests
1. Return QC Segment from an atypical, long QC Segment interval
2. ~~Return QC Segment crossing the boundary between two analyst intervals~~
3. Return empty when no QC Segments exist for requested channels and time range
4. ~~Returns both short and long QC Segments~~
5. ~~Returns two overlapping QC Segments~~
6. ~~Returns analyst-rejected masks~~
7. ~~Returns a single-sample QC Segment~~
8. Return QC Segment with 10 versions - default faceting
9. Return QC Segments with 10 version - fully populated versions
10. Return QC Segments from two different channels
