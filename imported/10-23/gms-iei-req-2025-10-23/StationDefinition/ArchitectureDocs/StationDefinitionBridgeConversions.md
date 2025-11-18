# Raw Station Definition COI – Data Bridge Conversions

This document describes how the GMS developed data bridge loaded and
converted the legacy USDNC format raw Station Definition records into
COI format **StationGroup**, **Station**, **ChannelGroup**, **Channel**,
and **Response** objects. Since the Data Fabric now provides the data
bridge, this document is provided only as a reference. It will not be
updated if the COI data models changes, the legacy USNDC format database
structure changes, etc. The class structures described in this document
may differ from the current COI data model documentation. If this
occurs, the COI data model documentation describes the current class
structures.

<table>
<colgroup>
<col style="width: 11%" />
<col style="width: 33%" />
<col style="width: 21%" />
<col style="width: 18%" />
<col style="width: 15%" />
</colgroup>
<thead>
<tr>
<th>Station Definition Object</th>
<th>Changes that create a new version</th>
<th>COI attribute -&gt; GMS DB mapping</th>
<th><p>Governing Rules/ Assumptions</p>
<p>****review governing overlap/timing rules that apply to all objects
below table</p></th>
<th>Relevant Notes</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Station Group</strong></td>
<td><p>Any changes to the values of any of the primitive type, value
object, or collection attributes defined in
the <strong>StationGroup</strong> class result in a
new <strong>StationGroup</strong> version:</p>
<ol type="1">
<li><p><em>description</em></p></li>
<li><p><em>effectiveUntil</em></p></li>
<li><p><em>stations</em> </p>
<ul>
<li><p>Changes to which <strong>Station</strong> entities
a <strong>StationGroup</strong> aggregates in
its <em>stations </em>collection require creating a
new <strong>StationGroup</strong> entity version.
A <strong>Station</strong> entity is uniquely identified by
its <em>name </em>and a <strong>StationGroup</strong> needs a new entity
version when the <em>name</em>s of the <strong>Stations</strong> in
its <em>stations</em> collection change since this
indicates <strong>Station</strong> entities have been added or removed
from the <strong>StationGroup</strong>.</p></li>
</ul></li>
</ol></td>
<td><ul>
<li><p><em>name:</em> network.net</p></li>
<li><p><em>effectiveAt:</em> dictated by versioning rules, see
‘Governing Rules/Assumptions’ column for more information</p></li>
<li><p><em>effectiveUntil:</em> dictated by versioning rules, see
‘Governing Rules/Assumptions’ column for more information</p></li>
<li><p><em>effectiveForRequestTime:</em> currently not
implemented</p></li>
<li><p><em>description:</em></p></li>
<li><p><em>stations</em> object (version reference for single time
query, entity references for time range query)</p>
<ul>
<li><p><em>name:</em> site.name</p></li>
<li><p><em>effectiveAt:</em> dictated by versioning rules, see
‘Governing Rules/Assumptions’ column for more information</p></li>
</ul></li>
</ul></td>
<td><ul>
<li><p>effectiveAt:</p></li>
<li><p>If initial station, network.on_date checked to determine if
earlier than the first affiliation.sta’s affiliation.time or any changes
in the station versioning that could cause that time to be different
from the affiliation time. The latest change is chosen that is still
before or at effectiveAt (i.e., if affiliation.time is later than
network.on_date it is used, if network.on_date is later than affiliation
it's used; i.e., whichever is closest to effectiveAt time within query).
Governing rules are the following to make that decision:</p></li>
<li><p>For a station to be added to a station group it requires that the
station could actually be built during that affiliation.time or it's
start time will be dictated by the following:</p></li>
<li><p>Site record needs to exist</p></li>
<li><p>Sitechan records need to exist (because requires that
allRawChannels object exists (which contain channels))</p></li>
<li><p>Channels require a sample rate to be created and thus require the
existence of either a sensor &amp; instrument table to access
instrument.samprate or the existence of a wfdisc record to access the
wfdisc.samprate</p></li>
<li><p>Thus, effectiveAt will be populated from the affiliation.time if
after site.ondate</p></li>
<li><p>If site.ondate after affiliation.time, site.ondate is used to
populate effectiveAt</p></li>
<li><p>If site.ondate before sitechan.ondate, sitechan.ondate will be
used to populate effectiveAt</p></li>
<li><p>If sample rate is after either of those times (or the same day as
site/sitechan), it’ll be used to populate the effectiveAt instead as it
is more precise</p></li>
<li><p>effectiveAt will always use the most precise time possible if the
times are the same across the tables (i.e., epoch time will be chosen
over julian day if possible)</p></li>
</ul>
<ul>
<li><p>Same versioning rules apply for effectiveUntil, except uses
whatever the time of the next change is, so it will be the earliest
change time after effectiveAt is to ensure validity of the station’s
existence</p></li>
</ul></td>
<td><ol type="1">
<li><p>A <strong>StationGroup’s </strong> <em>name </em> cannot change
because it is the  <strong>StationGroup </strong>entity
identifier.</p></li>
<li><p>Changes to attribute values within the  <strong>Station</strong> 
objects a  <strong>StationGroup</strong>  aggregates in
its <em>stations </em> collection do not result in a
new <strong>StationGroup</strong>  entity version.</p></li>
</ol></td>
</tr>
<tr>
<td><strong>Station</strong></td>
<td><p>Any changes to the values of any of the primitive type, value
object, or collection attributes defined in
the <strong>Station </strong>class result in a
new <strong>Station</strong> version:</p>
<ul>
<li><p><em>effectiveUntil</em></p></li>
<li><p><em>description</em></p></li>
<li><p><em>location</em></p></li>
<li><p><em>relativePositionsByChannel</em></p></li>
<li><p><em>type</em></p></li>
<li><p><em>allRawChannels</em></p>
<ul>
<li><p>Changes to which <strong>Channel</strong> entities
a <strong>Station</strong> aggregates in
its <em>allRawChannels </em>collection require creating a
new <strong>Station </strong>entity version.
A <strong>Channel</strong> entity is uniquely identified by
its <em>name </em>and a <strong>Station</strong> needs a new entity
version when the <em>name</em>s of the <strong>Channels</strong> in
its <em>allRawChannels</em> collection change since this
indicates <strong>Channel</strong> entities have been added or removed
from the <strong>Station</strong>.</p></li>
</ul></li>
<li><p><em>channelGroups</em> </p>
<ul>
<li><p>Changes to which <strong>ChannelGroup</strong> entities
a <strong>Station</strong> aggregates in
its <em>channelGroups </em>collection require creating a
new <strong>Station</strong> entity version.
A <strong>ChannelGroup</strong> entity is uniquely identified by
its <em>name </em>and a <strong>Station</strong> needs a new entity
version when the <em>name</em>s of the <strong>ChannelGroups</strong> in
its <em>channelGroups</em> collection change since this
indicates <strong>ChannelGroup</strong> entities have been added or
removed from the <strong>Station.</strong></p></li>
</ul></li>
</ul></td>
<td><ul>
<li><p><em>name:</em> site.name</p></li>
</ul>
<ul>
<li><p><em>effectiveAt:</em> dictated by versioning rules, see
‘Governing Rules/Assumptions’ column for more information</p></li>
<li><p><em>effectiveUntil:</em> dictated by versioning rules, see
‘Governing Rules/Assumptions’ column for more information</p></li>
</ul>
<ul>
<li><p><em>effectiveForRequestTime:</em> currently not
implemented</p></li>
<li><p><em>description:</em> site.staname</p></li>
<li><p><em>location:</em> (latitudeDegrees = site.lat;
longitudeDegrees=site.lon; depthKm=0; elevationKm= site.elev);</p></li>
<li><p><em>relativePositionsByChannel:</em> northDisplacementKm =
site.dnorth; eastDisplacementKm=site.deast; verticalDisplacementKm = 0);
version references for single time query, entity references for time
range query</p></li>
<li><p><em>type:</em> site.statype</p></li>
</ul>
<ul>
<li><p><em>allRawChannels:</em> (version reference for single time
query, entity reference for time range query; name =
(site.refsta).(sitchan.sta).(sitechan.chan), effectiveAt dictated by
versioning rules, see ‘Governing Rules/Assumptions’ column for more
information; refer to channel naming guidelines for more
information</p></li>
</ul>
<ul>
<li><p><em>ChannelGroups:</em> fully populated channel group (see below
for attribute mapping), associated channel objects are version
references for single time query and entity references for time range
query (see below for attribute mapping)</p></li>
</ul></td>
<td><ul>
<li><p>effectiveAt:</p></li>
<li><p>Dictated by any changes to attributes that would create a new
version, for the new version to exist:</p></li>
<li><p>It requires that the station could actually be built during the
site.ondate or it's start time will be dictated by the
following:</p></li>
<li><p>Sitechan records need to exist (because requires that
allRawChannels object exists (which contain channels))</p></li>
<li><p>Channels require a sample rate to be created and thus require the
existence of either a sensor &amp; instrument table to access
instrument.samprate or the existence of a wfdisc record to access the
wfdisc.samprate</p></li>
<li><p>Thus, effectiveAt will be populated from the site.ondate if
earliest otherwise will be populated from sitechan.ondate</p></li>
<li><p>If sample rate is after either of those times (or the same day as
site/sitechan times), it’ll be used to populate the effectiveAt time
instead as it is more precise; channel versioning time may also be
affected by response (see response versioning section below)</p></li>
<li><p>effectiveAt will always use the most precise time possible if the
times are the same across the tables (i.e., epoch time will be chosen
over julian day if possible)</p></li>
<li><p>Same versioning rules apply for effectiveUntil, except uses
whatever the time of the next change is, so it will be the earliest
change time after effectiveAt is to ensure validity of the station’s
existence</p></li>
<li><p>Channel effectiveAt time in allRawChannels (if not entity
reference) will be dictated by governing rules for channel (see channel
versioning and response sections below)</p></li>
<li><p>Channel group effectiveAt/effectiveUntil times will be dictated
by governing rules for channel group (see channel group versioning
section below)</p></li>
</ul></td>
<td><ol type="1">
<li><p>A <strong>Station’s </strong><em>name </em> cannot change because
it is the  <strong>Station </strong> entity identifier.</p></li>
<li><p>Changes to attribute values within the 
<strong>ChannelGroup</strong>  objects a <strong>Station</strong> 
aggregates in its <em>channelGroups </em> collection do not result in a
new  <strong>Station</strong>  entity version.</p></li>
<li><p>Changes to attribute values within the  <strong>Channel</strong> 
objects a <strong>Station</strong>  aggregates in its 
<em>allRaw</em>C<em>hannels </em> collection do not result in a new 
<strong>Station</strong>  entity version.</p></li>
</ol></td>
</tr>
<tr>
<td><strong>Channel Group</strong></td>
<td><p>Any changes to the values of any of the primitive type, value
object, or collection attributes defined in
the <strong>ChannelGroup</strong> class will result in a
new <strong>ChannelGroup</strong> version:</p>
<ol type="1">
<li><p><em>channelGroupType</em></p></li>
<li><p><em>description</em></p></li>
<li><p><em>effectiveUntil</em></p></li>
<li><p><em>location</em></p></li>
<li><p><em>channels</em> </p>
<ul>
<li><p>Changes to which <strong>Channel</strong> entities
a <strong>ChannelGroup</strong> aggregates in
its <em>channels </em>collection require creating a
new <strong>ChannelGroup</strong> entity version.
A <strong>Channel</strong> entity is uniquely identified by
its <em>name </em>and a <strong>ChannelGroup</strong> needs a new entity
version when the <em>name</em>s of the <strong>Channels</strong> in
its <em>channels</em> collection change since this
indicates <strong>Channel</strong> entities have been added or removed
from the <strong>ChannelGroup</strong>.</p></li>
</ul></li>
</ol></td>
<td><ul>
<li><p><em>name:</em> site.name</p></li>
</ul>
<ul>
<li><p><em>effectiveAt:</em> dictated by versioning rules, see
‘Governing Rules/Assumptions’ column for more information</p></li>
<li><p><em>effectiveUntil:</em> dictated by versioning rules, see
‘Governing Rules/Assumptions’ column for more information</p></li>
</ul>
<ul>
<li><p><em>effectiveForRequestTime:</em> currently not
implemented</p></li>
<li><p><em>description:</em> site.staname</p></li>
<li><p><em>location:</em> (latitudeDegrees = site.lat; longitudeDegrees=
site.lon; depthKm= sitechan.edepth; elevationKm= site.elev)</p>
<ul>
<li><p><em><strong>Note: channel group depth is set by taking the
average of all the sitechans that existed during that
time</strong></em></p></li>
</ul></li>
<li><p><em>channelGroupType:</em> GMS specific enumeration of
PHYSICAL_SITE or PROCESSING_GROUP, no direct mapping to CSS</p></li>
</ul>
<ul>
<li><p><em>channels:</em> version references for single time query,
entity references for time range query; name =
(site.refsta).(sitchan.sta).(sitechan.chan), effectiveAt dictated by
versioning rules, see ‘Governing Rules/Assumptions’ column for more
information; refer to channel naming guidelines for more
information</p></li>
</ul></td>
<td><ul>
<li><p>effectiveAt:</p></li>
<li><p>Dictated by any changes to attributes that would create a new
version, for the new version to exist:</p></li>
<li><p>It requires that the site could actually be built during the
site.ondate or it's start time will be dictated by the
following:</p></li>
<li><p>Sitechan records need to exist as channels need to exist for the
site to be built</p></li>
<li><p>Channels require a sample rate to be created and thus require the
existence of either a sensor &amp; instrument table to access
instrument.samprate or the existence of a wfdisc record to access the
wfdisc.samprate</p></li>
<li><p>Thus, effectiveAt will be populated from the site.ondate if
earliest otherwise will be populated from sitechan.ondate, i.e.,
channel’s effective time will be the time closest to the query time that
doesn’t exceed it. So, if a sitechan change time occurs after a site
change time (but before the query time), the sitechan time would be
chosen for the effectiveAt.</p></li>
<li><p>If sample rate is after either of those times (or the same day as
site/sitechan times), it’ll be used to populate the effectiveAt time
instead; channel versioning time may also be affected by response (see
response versioning section below)</p></li>
<li><p>effectiveAt will always use the most precise time possible if the
times are the same across the tables (i.e., epoch time will be chosen
over julian day if possible)</p></li>
<li><p>Same versioning rules apply for effectiveUntil, except uses
whatever the time of the next change is, so it will be the earliest
change time after effectiveAt is to ensure validity of the channel
group’s existence</p></li>
<li><p>Channel effectiveAt time (if not entity reference) will be
dictated by governing rules for channel (see channel versioning and
response sections below)</p></li>
</ul></td>
<td><ol type="1">
<li><p>A <strong>ChannelGroup’s </strong> <em>name </em> cannot change
because it is the <strong>ChannelGroup </strong> entity
identifier.</p></li>
<li><p>Changes to attribute values within the  <strong>Channel</strong> 
objects a <strong>ChannelGroup </strong> aggregates in its 
<em>channels </em> collection do not result in a new 
<strong>ChannelGroup </strong> entity version.</p></li>
</ol></td>
</tr>
<tr>
<td><strong>Channel</strong></td>
<td><p>Any changes to the values of any of the primitive type, value
object, or collection attributes defined in
the <strong>Channel</strong> class will result in a
new <strong>Channel </strong>version:</p>
<ol type="1">
<li><p><em>bandType</em></p></li>
<li><p><em>canonicalName</em></p></li>
<li><p><em>channelOrientationCode</em></p></li>
<li><p><em>configuredInputs</em></p>
<ul>
<li><p>Changes to which <strong>Channel</strong> entities
a <strong>Channel</strong> aggregates in
its <em>configuredInputs </em>collection require creating a
new <strong>Channel </strong>entity version.
A <strong>Channel</strong> entity is uniquely identified by
its <em>name </em>and a <strong>Channel</strong> needs a new entity
version when the <em>name</em>s of the <strong>Channels</strong> in
its <em>configuredInputs </em>collection change since this
indicates <strong>Channel</strong> entities have been added or removed
from the <strong>Channel’s</strong> <em>configuredInputs</em>.</p></li>
</ul></li>
<li><p><em>dataType</em></p></li>
<li><p><em>description</em></p></li>
<li><p><em>effectiveUntil</em></p></li>
<li><p><em>instrumentType</em></p></li>
<li><p><em>location</em></p></li>
<li><p><em>nominalSampleRateHz</em></p></li>
<li><p><em>orientationAngles</em></p></li>
<li><p><em>orientationType</em></p></li>
<li><p><em>processingDefinition</em></p></li>
<li><p><em>processingMetadata</em></p></li>
<li><p><em>response</em> </p>
<ul>
<li><p>Changes to which <strong>Response</strong> entity
a <strong>Channel</strong> aggregates in its <em>response </em>attribute
require creating a new <strong>Channel </strong>entity version.
A <strong>Response</strong> entity is uniquely identified by
its <em>id </em>and a <strong>Channel</strong> needs a new entity
version when the <em>id</em> of the <strong>Response</strong> in
its <em>response</em> attribute changes since this indicates
the <strong>Response</strong> entity within
the <strong>Channel </strong>has been added, removed, or
replaced.</p></li>
</ul></li>
<li><p><em>station  </em></p>
<ul>
<li><p>Changes to which <strong>Station </strong>entity
a <strong>Channel</strong> aggregates in its <em>station </em>attribute
require creating a new <strong>Channel</strong> entity version.
A <strong>Station</strong> entity is uniquely identified by
its <em>name </em>and a <strong>Channel</strong> needs a new entity
version when the <em>name</em> of the <strong>Station</strong> in
its <em>station</em> attribute changes since this indicates
the <strong>Station</strong> entity within
the <strong>Channel </strong>has been replaced.</p></li>
</ul></li>
<li><p><em>units</em></p></li>
</ol></td>
<td><ul>
<li><p><em>name:</em> sitechan.name</p></li>
</ul>
<ul>
<li><p><em>effectiveAt:</em> dictated by versioning rules, see
‘Governing Rules/Assumptions’ column for more information</p></li>
<li><p><em>effectiveUntil:</em> dictated by versioning rules, see
‘Governing Rules/Assumptions’ column for more information</p></li>
<li><p><em>effectiveForRequestTime:</em> currently not
implemented</p></li>
<li><p><em>canonicalName</em>*</p></li>
<li><p><em>description</em>: sitechan.descrip</p></li>
<li><p><em>channelOrientationCode</em>*</p></li>
<li><p><em>nominalSampleRateHz</em>: either wfdisc.samprate or
instrument.samprate, but instrument table checked first</p></li>
<li><p><em>processingDefinition:</em> No direct mapping to CSS, see Arch
guidance link for more information**</p></li>
<li><p><em>processingMetadata:</em> No direct mapping to CSS, see Arch
guidance link for more information**</p></li>
<li><p><em>configuredInputs:</em> No direct mapping to CSS, empty for
raw channels, see Arch guidance link for more information**; single time
query and populated, populated as version references, time range query
and populated, populated as entity references</p></li>
<li><p><em>units:</em> No direct mapping to CSS. An enumeration exists
for seismic (nm), hydro (μPa), infrasound (Pa) data, see Arch guidance
link for more information**</p></li>
<li><p><em>bandType*</em></p></li>
<li><p><em>instrumentType*</em></p></li>
<li><p><em>orientationType*</em></p></li>
<li><p><em>datatype*</em></p></li>
<li><p><em>location:</em> (latitudeDegrees = site.lat; longitudeDegrees=
site.lon; depthKm= sitechan.edepth; elevationKm= site.elev)</p></li>
<li><p><em>orientationAngles:</em> (horizontalAngle: sitechan.hang;
verticalAngle: sitechan.vang)</p></li>
<li><p><em>station:</em> version reference for single time query, entity
reference for time range query; name=site.sta, effectiveAt dictated by
versioning rules, see ‘Governing Rules/Assumptions’ column for more
information</p></li>
<li><p><em>response:</em> see attributes below, fully populated for
single time query with FrequencyAmplitudePhase object for fapResponse
attribute as a by-id reference, otherwise entity reference for time
range query; id = internally generated UUID, effectiveAt dictated by
versioning rules, see ‘Governing Rules/Assumptions’ column for more
information</p></li>
</ul></td>
<td><ul>
<li><p>effectiveAt:</p></li>
<li><p>Dictated by any changes to attributes that would create a new
version, for the new version to exist:</p></li>
<li><p>It requires that the channel could actually be built during the
sitechan.ondate or it's start time will be dictated by the
following:</p></li>
<li><p>Channels require a sample rate to be created and thus require the
existence of either a sensor &amp; instrument table to access
instrument.samprate or the existence of a wfdisc record to access the
wfdisc.samprate</p></li>
<li><p>Adding/removing a response would create a new channel version, so
those changes may influence the effectiveAt time (see response
versioning information rules below to see impacts on channel versioning,
only affected though by addition or removal of new response to the
channel version)</p></li>
<li><p>We only ever remove a response if we have verifiable evidence
that the sensor/instrument doesn’t exist anymore, i.e., it is not based
on the absence of or a gap in wfdisc records. This is to prohibit sets
of response versions from being generated when there is a gap in wfdisc
records that may be due to transmission issues but the channel still
continues to exist. This is also because the lack of information doesn’t
preclude the need to remove, we just don’t have any data to know what’s
happening between the gaps definitely</p></li>
<li><p>Reminder for the channel to a exist it must be related to a
station, so that requires the existence of a site record during the
channel version’s existence. If station is a version reference,
effectiveAt will be dictated by station versioning rules noted above. It
also must have corresponding site records to have a location, so a site
must exist during the channel’s existence for a channel version to exist
as well</p></li>
<li><p>effectiveAt will always use the most precise time possible if the
times are the same across the tables (i.e., epoch time will be chosen
over julian day if possible)</p></li>
<li><p>Same versioning rules apply for effectiveUntil, except uses
whatever the time of the next change is, so it will be the earliest
change time after effectiveAt is to ensure validity of the channel’s
existence</p></li>
</ul></td>
<td><ol type="1">
<li><p>A  <strong>Channel’s </strong><em>name </em> cannot change
because it is the  <strong>Channel </strong> entity identifier.</p></li>
<li><p>Changes to attribute values within
the <strong>Response</strong> object a <strong>Channel </strong>
aggregates in its  <em>response </em> attribute do not result in a new 
<strong>Channel </strong> version.</p></li>
<li><p>Changes to attribute values within the  <strong>Station</strong> 
object a <strong>Channel </strong> aggregates in
its <em>station </em>attribute do not result in a new 
<strong>Channel </strong> version.</p></li>
<li><p>Changes to attribute values within the  <strong>Channel</strong> 
objects a <strong>Channel </strong> aggregates in its 
<em>configuredInputs </em> collection do not result in a new 
<strong>Channel </strong> version.</p></li>
</ol></td>
</tr>
<tr>
<td><strong>Response</strong></td>
<td><p>Any changes to the values of any of the primitive type or value
object attributes defined in the <strong>Response</strong> class will
result in a new <strong>Response</strong> version</p>
<ol type="1">
<li><p><em>calibrationFactor.standardDeviation</em></p></li>
<li><p><em>calibrationFactor.units</em></p></li>
<li><p><em>calibrationFactor.value</em></p></li>
<li><p><em>calibrationPeriodSec</em></p></li>
<li><p><em>calibrationTimeShift</em></p></li>
<li><p><em>effectiveUntil</em></p></li>
<li><p><em>fapResponse</em></p>
<ol type="a">
<li><p>Changes to which <strong>FrequencyAmplitudePhase</strong> value
object a <strong>Response</strong> aggregates in
its <em>fapResponse </em>attribute require creating a
new <strong>Response</strong> entity version.
Each <strong>FrequencyAmplitudePhase</strong> object is uniquely
identified by its <em>id </em>and a <strong>Response </strong>needs a
new version when the <em>id</em> of
the <strong>FrequencyAmplitudePhase</strong> in
its <em>fapResponse</em> attribute changes since this indicates
the <strong>FrequencyAmplitudePhase</strong> object within
the <strong>Response </strong>has been added, removed, or
replaced.</p></li>
<li><p><strong>FrequencyAmplitudePhase</strong> is a value object class.
Any changes to any of its attributes will result in a
new <strong>FrequencyAmplitudePhase</strong> object with a
new <em>id</em>.</p></li>
</ol></li>
</ol></td>
<td><ul>
<li><p><em>id:</em> No direct mapping to CSS; internally generated UUID;
see response and calibration COI:</p></li>
</ul>
<ul>
<li><p><em>effectiveAt:</em> dictated by versioning rules, see
‘Governing Rules/Assumptions’ column for more information</p></li>
<li><p><em>effectiveUntil:</em> dictated by versioning rules, see
‘Governing Rules/Assumptions’ column for more information</p></li>
</ul>
<ul>
<li><p><em>calibrationPeriodSec</em>: wfdisc.calper</p></li>
<li><p><em>calibrationTimeShift:</em> sensor.tshift</p></li>
<li><p><em>calibrationFactor.value:</em> wfdisc.calib</p></li>
<li><p><em>calibrationFactor.standardDeviation:</em> no direct mapping
to CSS, set to 0</p></li>
<li><p><em>calibrationFactor.units:</em> For USNDC P3 schema, units are
always nm/count</p></li>
<li><p><em>fapResponse:</em></p>
<ul>
<li><p>id: No direct mapping to CSS; internally generated UUID, see link
in previous ID field for more information on COI</p></li>
<li><p>response file comes from instrument.dir, instrument.dfile can be
used to populated frequencyAmplitudePhase object***</p></li>
</ul></li>
</ul></td>
<td><ul>
<li><p>effectiveAt:</p></li>
<li><p>Dictated by any changes to attributes that would create a new
version, for the new version to exist:</p></li>
<li><p>A response doesn’t exist without a channel, so a channel has to
be able to be built during the response version for a response to be
created (see channel versioning rules above)</p></li>
<li><p>Responses require the existence of wfdisc, sensor, and instrument
table records to populate the calibrationPeriodSec (wfdisc),
calibrationTimeShift (sensor), value, and the appropriate references to
the dfile/dir (instrument) to eventually be able to create the
AmplitudePhaseResponse objects and thus the time in wfdisc &amp; sensor
will dictate the versioning, whichever one is sooner. Since wfdisc and
sensor records both use epoch times they are of equal
precision.</p></li>
<li><p>We only ever remove a response if we have verifiable evidence
that the sensor/instrument doesn’t exist anymore, i.e., it is not based
on the absence of or a gap in wfdisc records. This is to prohibit sets
of response versions from being generated when there is a gap in wfdisc
records that may be due to transmission issues but the channel still
continues to exist. This is also because the lack of information doesn’t
preclude the need to remove, we just don’t have any data to know what’s
happening between the gaps definitely</p></li>
<li><p>Same versioning rules apply for effectiveUntil, except uses
whatever the latest date is to ensure validity of the response’s
existence</p></li>
</ul></td>
<td><ol type="1">
<li><p>A <strong>Response’s </strong><em>id </em> cannot change because
it is the  <strong>Response </strong> entity identifier.</p></li>
<li><p>(04/01/2025) Response.calibration is optional, so a Response 
object may be created for a time range without a wfdisc entry, 
resulting in a Response which includes a fapResponse but not a 
calibration.</li></p>
</ol></td>
</tr>
</tbody>
</table>

\*\*\*\* When database records overlap in areas where new versions would
be created, e.g., a site record that ends and a new site record that
begins on the same Julian day (i.e., both end and start on 2019005),
using this example, the previous version will end on 2019 005
11:59:59.999999 and the new version will begin at 2019 005 12:00:00,
such that there is a 1ms gap between the versions. For all other cases,
when a record begins on that day where a new version would be created
the version will start at 00:00:00 or where a record ends on that day
where a new version would be created the version will end at
23:59:59.999999. This is true, barring other records with more precision
(e.g., sensor, etc.) exist at the same time which could offer us an
effectiveAt/effectiveUntil for the new version. We will use whatever the
highest precision record is for timing.
