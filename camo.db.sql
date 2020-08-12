BEGIN TRANSACTION;
DROP TABLE IF EXISTS "machines";
CREATE TABLE IF NOT EXISTS "machines" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR,
	"max_rpm"	INTEGER,
	"spot"	VARCHAR,
	"drill"	VARCHAR,
	"tap"	VARCHAR,
	"peck"	VARCHAR,
	"ream"	VARCHAR,
	"drill_format"	VARCHAR,
	"tap_format"	VARCHAR,
	"program_start"	VARCHAR,
	"program_end"	VARCHAR,
	"tool_start"	VARCHAR,
	"tool_end"	VARCHAR,
	"op_start"	VARCHAR,
	"countersink"	VARCHAR,
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "camo_ops";
CREATE TABLE IF NOT EXISTS "camo_ops" (
	"id"	INTEGER NOT NULL,
	"op_type"	VARCHAR,
	"function"	VARCHAR,
	"priority"	VARCHAR,
	"feature_type_id"	INTEGER,
	PRIMARY KEY("id"),
	FOREIGN KEY("feature_type_id") REFERENCES "feature_types"("id")
);
DROP TABLE IF EXISTS "features";
CREATE TABLE IF NOT EXISTS "features" (
	"name"	VARCHAR UNIQUE,
	"id"	INTEGER NOT NULL,
	"description"	VARCHAR,
	"feature_type_id"	INTEGER,
	PRIMARY KEY("id"),
	FOREIGN KEY("feature_type_id") REFERENCES "feature_types"("id")
);
DROP TABLE IF EXISTS "feature_types";
CREATE TABLE IF NOT EXISTS "feature_types" (
	"id"	INTEGER NOT NULL,
	"feature_type"	VARCHAR UNIQUE,
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "operations";
CREATE TABLE IF NOT EXISTS "operations" (
	"id"	INTEGER NOT NULL,
	"feature_id"	INTEGER,
	"tool_id"	INTEGER,
	"camo_op_id"	INTEGER,
	"peck"	DECIMAL,
	"feed"	DECIMAL,
	"speed"	DECIMAL,
	PRIMARY KEY("id"),
	FOREIGN KEY("feature_id") REFERENCES "features"("id"),
	FOREIGN KEY("camo_op_id") REFERENCES "camo_ops"("id"),
	FOREIGN KEY("tool_id") REFERENCES "tools"("id")
);
DROP TABLE IF EXISTS "tools";
CREATE TABLE IF NOT EXISTS "tools" (
	"id"	INTEGER NOT NULL,
	"qb_id"	INTEGER UNIQUE,
	"tool_type_id"	INTEGER,
	"tool_number"	INTEGER,
	"name"	VARCHAR,
	"diameter"	DECIMAL,
	"number_of_flutes"	INTEGER,
	"pitch"	DECIMAL,
	PRIMARY KEY("id"),
	FOREIGN KEY("tool_type_id") REFERENCES "tool_types"("id")
);
DROP TABLE IF EXISTS "tool_types";
CREATE TABLE IF NOT EXISTS "tool_types" (
	"id"	INTEGER NOT NULL,
	"tool_type"	VARCHAR,
	PRIMARY KEY("id")
);
INSERT INTO "machines" VALUES (1,'Femco',2500,'81','81','84','83','81','G98 G{code} Z{depth} R{r_plane} F{feed}
{points}
G80','G95
M29 S{speed}
G98 G{code} Z{depth} R{r_plane} F{pitch}
{points}
G80
G94','%
O{program_number} ( {program_comment} )
{tool_list}
G20
G0G17G40G49G80G90
M64
G90B0.','M9
M5
G91 G28 Z0.
M30
%','( {tool_name} )
G0 G90 G{work_offset} X{x} Y{y} {spindle}
G90 G{work_offset} W0.
G43 H{tool_number} Z{clearance} {coolant}','M5
G91 G28 Z0. M9
G91 G28 W0.
M01','G0 Z{clearance}
X{x} Y{y} {spindle}','81');
INSERT INTO "machines" VALUES (2,'Planer',250,'81','81','84','81','81','G98 G{code} Z{depth} R{r_plane} F{feed}
{points}
G80','M29 S{speed}
G98 G{code} Z{depth} R{r_plane} F{feed}
{points}
G80','%
O{program_number} ( {program_comment} )
{tool_list}
G20
G00 G17 G40 G80 G49 G90 ','M5
M30
%','( {tool_name} )
G0 G90 G{work_offset} X{x} Y{y} {spindle}
G43 H{tool_number}
Z{clearance}','M5
M00','G0 Z{clearance}
X{x} Y{y} {spindle}','81');
INSERT INTO "machines" VALUES (3,'Nomura',2500,'81','81','84','83','81','G98 G{code} Z{depth} R{r_plane} F{feed}
{points}
G80','G95
M29 S{speed}
G98 G{code} Z{depth} R{r_plane} F{pitch}
{points}
G80
G94','%
O{program_number} ( {program_comment} )
{tool_list}
G20
G00 G17 G40 G80 G49 G90
M17
G90 B0.
M18','M9
M5
G91 G28 Z0.
M30
%','( {tool_name} )
G0 G90 G{work_offset} X{x} Y{y} {spindle}
G90 G{work_offset} W0.
G43 H{tool_number} Z{clearance} {coolant}
T{next_tool}','M5
G91 G28 Z0. M9
G91 G28 W0.
M01','G0 Z{clearance} {coolant}
X{x} Y{y} {spindle}','81');
INSERT INTO "machines" VALUES (4,'Toyoda',4000,'81','81','84','83','81','G98 G{code} Z{depth} R{r_plane} F{feed}
{points}
G80','G95
M29 S{speed}
G98 G{code} Z{depth} R{r_plane} F{pitch}
{points}
G80
G94','%
O{program_number} ( {program_comment} )
{tool_list}
G20
G0G17G40G49G80G90','M9
M5
G91 G28 Z0.
M30
%','( {tool_name} )
G0 G90 G{work_offset} X{x} Y{y} {spindle}
G90 G{work_offset}
G43 H{tool_number} Z{clearance} {coolant}','M5
G91 G28 Z0. M9
M01','G0 Z{clearance}
X{x} Y{y} {spindle}','81');
INSERT INTO "camo_ops" VALUES (1,'Face - R','face_rough','10',3);
INSERT INTO "camo_ops" VALUES (2,'Face - F','face_finish','20',3);
INSERT INTO "camo_ops" VALUES (3,'Spot','drill','30',1);
INSERT INTO "camo_ops" VALUES (4,'Drill','drill','40',1);
INSERT INTO "camo_ops" VALUES (5,'Peck','drill','40',1);
INSERT INTO "camo_ops" VALUES (6,'Countersink','drill','44',1);
INSERT INTO "camo_ops" VALUES (7,'Ream','drill','45',1);
INSERT INTO "camo_ops" VALUES (8,'Tap','drill','50',1);
INSERT INTO "camo_ops" VALUES (9,'Slot - R','slot_rough','60',2);
INSERT INTO "camo_ops" VALUES (10,'Slot - F','slot_finish','70',2);
INSERT INTO "features" VALUES ('Basic',1,'',3);
INSERT INTO "features" VALUES ('M8 x 1.25',2,'',1);
INSERT INTO "features" VALUES ('1/2-13',3,'',1);
INSERT INTO "features" VALUES ('3/8-16',4,'',1);
INSERT INTO "features" VALUES ('3/8 slot',5,'',2);
INSERT INTO "feature_types" VALUES (1,'Drilling');
INSERT INTO "feature_types" VALUES (2,'Slotting');
INSERT INTO "feature_types" VALUES (3,'Facing');
INSERT INTO "operations" VALUES (1,1,32,1,0,100,385);
INSERT INTO "operations" VALUES (2,1,33,2,0,24.43,509);
INSERT INTO "operations" VALUES (3,2,2,3,0,2,2000);
INSERT INTO "operations" VALUES (4,2,23,5,0.1,2.8,934);
INSERT INTO "operations" VALUES (5,2,12,8,0,10,203);
INSERT INTO "operations" VALUES (6,3,2,3,0,2,2000);
INSERT INTO "operations" VALUES (7,3,27,5,0.125,2.8,588);
INSERT INTO "operations" VALUES (8,3,19,8,0,10,130);
INSERT INTO "operations" VALUES (9,4,2,3,0,2,2000);
INSERT INTO "operations" VALUES (10,5,6,9,0,12.22,3056);
INSERT INTO "operations" VALUES (11,5,7,10,0,20.37,2546);
INSERT INTO "tools" VALUES (1,1351,5,22,'CDRL - 0.10938 - 1351',0.10938,1,0);
INSERT INTO "tools" VALUES (2,1361,5,1,'CDRL - 0.25 - 1361',0.25,1,0);
INSERT INTO "tools" VALUES (3,1363,7,2,'CSNK - 1 - 82 - 1363',1,1,0);
INSERT INTO "tools" VALUES (4,1481,3,26,'BULL - 0.1875 x 0.625 -CH - 1481',0.1875,4,0);
INSERT INTO "tools" VALUES (5,1483,3,25,'BULL - 0.25 x 0.75 x 0.03r - 1483',0.25,4,0);
INSERT INTO "tools" VALUES (6,1484,3,13,'BULL - 0.3125 x 0.75 x 0.03r - 1484',0.3125,4,0);
INSERT INTO "tools" VALUES (7,1485,3,12,'BULL - 0.375 x 0.875 x 0.03r - 1485',0.375,4,0);
INSERT INTO "tools" VALUES (8,1486,3,26,'BULL - 0.4375 x 1.125 x 0.015r - 1486',0.4375,4,0);
INSERT INTO "tools" VALUES (9,1487,3,27,'BULL - 0.5 x 1 x 0.03r - 1487',0.5,4,0);
INSERT INTO "tools" VALUES (10,1488,3,17,'BULL - 0.625 x 1.625 x 0.03r - 1488',0.625,4,0);
INSERT INTO "tools" VALUES (11,1489,3,18,'BULL - 0.75 x 1.5 x 0.015r - 1489',0.75,4,0);
INSERT INTO "tools" VALUES (12,1677,2,19,'CTAP - M8 x 1.25 - 6H - 1677',0.3149,1,0.0492);
INSERT INTO "tools" VALUES (13,1682,2,10,'CTAP - 1/4 x 20 - H3 - 1682',0.25,1,0.05);
INSERT INTO "tools" VALUES (14,1683,2,23,'CTAP - 5/16 x 18 - H3 - 1683',0.3125,1,0.0555);
INSERT INTO "tools" VALUES (15,1684,2,11,'CTAP - 3/8 x 16 - H3 - 1684',0.375,1,0.0625);
INSERT INTO "tools" VALUES (16,1688,2,20,'CTAP - 5/8 x 11 - H3 - 1688',0.625,1,0.0909);
INSERT INTO "tools" VALUES (17,1689,2,14,'CTAP - 3/4 x 10 - H3 - 1689',0.75,1,0.1);
INSERT INTO "tools" VALUES (18,1690,2,37,'CTAP - 7/8 x 9 - H4 - 1690',0.875,1,0.1111);
INSERT INTO "tools" VALUES (19,1703,2,15,'CTAP - 1/2 x 13 - H3 - 1703',0.5,1,0.07692);
INSERT INTO "tools" VALUES (20,1819,1,2,'DRIL - 0.201 - 1819',0.201,1,0);
INSERT INTO "tools" VALUES (21,1831,1,24,'DRIL - 0.257 - 1831',0.257,1,0);
INSERT INTO "tools" VALUES (22,1846,1,6,'DRIL - 0.368 - 1846',0.368,1,0);
INSERT INTO "tools" VALUES (23,1868,1,7,'DRIL - 0.2656 - 1868',0.2656,1,0);
INSERT INTO "tools" VALUES (24,1869,1,14,'DRIL - 0.2813 - 1869',0.2813,1,0);
INSERT INTO "tools" VALUES (25,1871,1,8,'DRIL - 0.3125 - 1871',0.3125,1,0);
INSERT INTO "tools" VALUES (26,1877,1,16,'DRIL - 0.4063 - 1877',0.4063,1,0);
INSERT INTO "tools" VALUES (27,1878,1,16,'DRIL - 0.4219 - 1878',0.4219,1,0);
INSERT INTO "tools" VALUES (28,1882,1,31,'DRIL - 0.4844 - 1882',0.4844,1,0);
INSERT INTO "tools" VALUES (29,1885,1,21,'DRIL - 0.5313 - 1885',0.5313,1,0);
INSERT INTO "tools" VALUES (30,1893,1,5,'DRIL - 0.6563 - 1893',0.6563,1,0);
INSERT INTO "tools" VALUES (31,1900,1,36,'DRIL - 0.7656 - 1900',0.7656,1,0);
INSERT INTO "tools" VALUES (32,1916,4,4,'HIFD - 6 - 1916',6,8,0);
INSERT INTO "tools" VALUES (33,1918,4,3,'FACE - 6 x 90 Deg - 1918',6,8,0);
INSERT INTO "tools" VALUES (34,2006,6,30,'REAM - 0.499 - 2006',0.499,6,0);
INSERT INTO "tools" VALUES (35,2122,6,9,'REAM - 0.3745 - 2122',0.3745,6,0);
INSERT INTO "tool_types" VALUES (1,'Drill');
INSERT INTO "tool_types" VALUES (2,'Tap');
INSERT INTO "tool_types" VALUES (3,'Endmill');
INSERT INTO "tool_types" VALUES (4,'Facemill');
INSERT INTO "tool_types" VALUES (5,'Spot');
INSERT INTO "tool_types" VALUES (6,'Reamer');
INSERT INTO "tool_types" VALUES (7,'Countersink');
COMMIT;
