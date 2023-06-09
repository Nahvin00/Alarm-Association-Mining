CREATE TABLE "RETIMIG"."AAA_ARM_ALARM_DATA" 
   (	"TAGNAME" VARCHAR2(500 BYTE), 
	"DESCRIPTION" VARCHAR2(1000 BYTE), 
	"AREA" VARCHAR2(500 BYTE), 
	"TYPE" VARCHAR2(500 BYTE), 
	"PRIORITY" VARCHAR2(500 BYTE), 
	"CATEGORY" VARCHAR2(500 BYTE), 
	"PROVIDER" VARCHAR2(500 BYTE)
   ) SEGMENT CREATION IMMEDIATE 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1
  BUFFER_POOL DEFAULT FLASH_CACHE DEFAULT CELL_FLASH_CACHE DEFAULT)
  TABLESPACE "TDAT" ;