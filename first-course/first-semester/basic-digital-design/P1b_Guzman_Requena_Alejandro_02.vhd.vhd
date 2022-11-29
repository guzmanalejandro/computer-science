---------------------
--TESTS INDIVIDUALS--
---------------------

-- TEST INVERSOR: --

ENTITY bdp_inversor IS
END bdp_inversor;

ARCHITECTURE senyals OF bdp_inversor IS

COMPONENT circuit0
PORT (a: IN BIT; z: OUT BIT);
END COMPONENT;
	
SIGNAL entrada,sortida: BIT;

FOR DUT0: circuit0 USE ENTITY WORK.inversor(logica);
-- DUT -> Device Under Test

BEGIN
DUT0: circuit0 PORT MAP (entrada,sortida);
PROCESS

BEGIN
entrada <= '0';
WAIT FOR 100 ns;
entrada <= '1';
WAIT FOR 500 ns;
entrada <= '0';
WAIT FOR 1000 ns;
entrada <= '1';

END PROCESS;
END senyals;

----------------
-- TEST AND2: --
----------------
ENTITY bdp_and2 IS
END bdp_and2;

ARCHITECTURE prova_and2 OF bdp_and2 IS

COMPONENT la_porta_and2
PORT (a,b: IN BIT; z: OUT BIT);
END COMPONENT;
 
SIGNAL ent1, ent2, sortida: BIT; 
FOR DUT1: la_porta_and2 USE ENTITY WORK.and2(logica);

BEGIN
DUT1: la_porta_and2 PORT MAP (ent1,ent2,sortida);

PROCESS (ent1,ent2)
BEGIN
ent1 <= NOT ent1 AFTER 50 ns;
ent2 <= NOT ent2 AFTER 100 ns;
END PROCESS;
END prova_and2;

----------------
-- TEST AND3: --
----------------
ENTITY bdp_and3 IS
END bdp_and3;

ARCHITECTURE prova_and3 OF bdp_and3 IS

COMPONENT la_porta_and3
PORT (a,b,c: IN BIT; z: OUT BIT);
END COMPONENT;
 
SIGNAL ent1, ent2, ent3, sortida: BIT; 

FOR DUT1: la_porta_and3 USE ENTITY WORK.and3(logica);

BEGIN
DUT1: la_porta_and3 PORT MAP (ent1,ent2,ent3,sortida);

PROCESS (ent1,ent2,ent3)
BEGIN
ent1 <= NOT ent1 AFTER 50 ns;
ent2 <= NOT ent2 AFTER 100 ns;
ent3 <= NOT ent3 AFTER 150 ns;
END PROCESS;
END prova_and3;

----------------
-- TEST AND4: --
----------------
ENTITY bdp_and4 IS
END bdp_and4;

ARCHITECTURE prova_and4 OF bdp_and4 IS

COMPONENT la_porta_and4
PORT (a,b,c,d: IN BIT; z: OUT BIT);
END COMPONENT;
 
SIGNAL ent1, ent2, ent3, ent4, sortida: BIT; 

FOR DUT1: la_porta_and4 USE ENTITY WORK.and4(logica);

BEGIN
DUT1: la_porta_and4 PORT MAP (ent1,ent2,ent3,ent4,sortida);

PROCESS (ent1,ent2,ent3,ent4)
BEGIN
ent1 <= NOT ent1 AFTER 50 ns;
ent2 <= NOT ent2 AFTER 100 ns;
ent3 <= NOT ent3 AFTER 150 ns;
ent4 <= NOT ent4 AFTER 200 ns;
END PROCESS;
END prova_and4;

---------------
-- TEST OR2: --
---------------
ENTITY bdp_or2 IS
END bdp_or2;

ARCHITECTURE prova_or2 OF bdp_or2 IS

COMPONENT la_porta_or2
PORT (a,b: IN BIT; z: OUT BIT);
END COMPONENT;
 
SIGNAL ent1, ent2, sortida: BIT; 
FOR DUT1: la_porta_or2 USE ENTITY WORK.or2(logica);

BEGIN
DUT1: la_porta_or2 PORT MAP (ent1,ent2,sortida);

PROCESS (ent1,ent2)
BEGIN
ent1 <= NOT ent1 AFTER 50 ns;
ent2 <= NOT ent2 AFTER 100 ns;
END PROCESS;
END prova_or2;


----------------
-- TEST OR3: --
----------------
ENTITY bdp_or3 IS
END bdp_or3;

ARCHITECTURE prova_or3 OF bdp_or3 IS

COMPONENT la_porta_or3
PORT (a,b,c: IN BIT; z: OUT BIT);
END COMPONENT;
 
SIGNAL ent1, ent2, ent3, sortida: BIT; 

FOR DUT1: la_porta_or3 USE ENTITY WORK.or3(logica);

BEGIN
DUT1: la_porta_or3 PORT MAP (ent1,ent2,ent3,sortida);

PROCESS (ent1,ent2,ent3)
BEGIN
ent1 <= NOT ent1 AFTER 50 ns;
ent2 <= NOT ent2 AFTER 100 ns;
ent3 <= NOT ent3 AFTER 150 ns;
END PROCESS;
END prova_or3;


---------------
-- TEST OR4: --
---------------
ENTITY bdp_or4 IS
END bdp_or4;

ARCHITECTURE prova_or4 OF bdp_or4 IS

COMPONENT la_porta_or4
PORT (a,b,c,d: IN BIT; z: OUT BIT);
END COMPONENT;
 
SIGNAL ent1, ent2, ent3, ent4, sortida: BIT; 

FOR DUT1: la_porta_or4 USE ENTITY WORK.or4(logica);

BEGIN
DUT1: la_porta_or4 PORT MAP (ent1,ent2,ent3,ent4,sortida);

PROCESS (ent1,ent2,ent3,ent4)
BEGIN
ent1 <= NOT ent1 AFTER 50 ns;
ent2 <= NOT ent2 AFTER 100 ns;
ent3 <= NOT ent3 AFTER 150 ns;
ent4 <= NOT ent4 AFTER 200 ns;
END PROCESS;
END prova_or4;

----------------
--Test conjunt--
----------------

ENTITY bdp_portes IS
END bdp_portes;

ARCHITECTURE test OF bdp_portes IS

-- INVERSOR--
COMPONENT inversor
PORT (a: IN BIT; z: OUT BIT);
END COMPONENT;

--INVERSOR RETARDAT--
COMPONENT inversor_retardat
PORT (a: IN BIT; z: OUT BIT);
END COMPONENT;

-- AND 2--
COMPONENT la_porta_and2
PORT (a,b: IN BIT; z: OUT BIT);
END COMPONENT;

--AND 2 RETARDAT--
COMPONENT la_porta_and2_retardada
PORT (a,b: IN BIT; z: OUT BIT);
END COMPONENT;

--AND 3--
COMPONENT la_porta_and3
PORT (a,b,c: IN BIT; z: OUT BIT);
END COMPONENT;

--AND 3 RETARDAT--
COMPONENT la_porta_and3_retardada
PORT (a,b,c: IN BIT; z: OUT BIT);
END COMPONENT;

--AND 4--
COMPONENT la_porta_and4
PORT (a,b,c,d: IN BIT; z: OUT BIT);
END COMPONENT;

--AND 4 RETARDAT--
COMPONENT la_porta_and4_retardada
PORT (a,b,c,d: IN BIT; z: OUT BIT);
END COMPONENT;

--OR 2--
COMPONENT la_porta_or2
PORT (a,b: IN BIT; z: OUT BIT);
END COMPONENT;

--OR 2 RETARDAT--
COMPONENT la_porta_or2_retardada
PORT (a,b: IN BIT; z: OUT BIT);
END COMPONENT;

--OR 3--
COMPONENT la_porta_or3
PORT (a,b,c: IN BIT; z: OUT BIT);
END COMPONENT;

--OR 3 RETARDAT--
COMPONENT la_porta_or3_retardada
PORT (a,b,c: IN BIT; z: OUT BIT);
END COMPONENT;

--OR 4--
COMPONENT la_porta_or4
PORT (a,b,c,d: IN BIT; z: OUT BIT);
END COMPONENT;

--OR 4 RETARDAT
COMPONENT la_porta_or4_retardada
PORT (a,b,c,d: IN BIT; z: OUT BIT);
END COMPONENT;

--XOR 2--
COMPONENT la_porta_xor2
PORT (a,b: IN BIT; z: OUT BIT);
END COMPONENT;

--XOR 2 RETARDAT
COMPONENT la_porta_xor2_retardada
PORT (a,b: IN BIT; z: OUT BIT);
END COMPONENT;

SIGNAL ent1, ent2, ent3, ent4, sortida_and2, sortida_ret_and2, sortida_and3, sortida_ret_and3, sortida_and4, sortida_ret_and4, 
sortida_or2, sortida_ret_or2, sortida_or3, sortida_ret_or3, sortida_or4, sortida_ret_or4, sortida_inversor, sortida_ret_inversor,
sortida_xor2, sortida_ret_xor2: BIT; 

FOR DUT0: inversor USE ENTITY WORK.inversor(logica);
FOR DUT1: la_porta_and2 USE ENTITY WORK.and2(logica);
FOR DUT2: la_porta_and3 USE ENTITY WORK.and3(logica);
FOR DUT3: la_porta_and4 USE ENTITY WORK.and4(logica);
FOR DUT4: la_porta_or2 USE ENTITY WORK.or2(logica);
FOR DUT5: la_porta_or3 USE ENTITY WORK.or3(logica);
FOR DUT6: la_porta_or4 USE ENTITY WORK.or4(logica);

FOR DUT7: la_porta_and2_retardada USE ENTITY WORK.and2(logicaretard);
FOR DUT8: la_porta_and3_retardada USE ENTITY WORK.and3(logicaretard);
FOR DUT9: la_porta_and4_retardada USE ENTITY WORK.and4(logicaretard);
FOR DUT10: la_porta_or2_retardada USE ENTITY WORK.or2(logicaretard);
FOR DUT11: la_porta_or3_retardada USE ENTITY WORK.or3(logicaretard);
FOR DUT12: la_porta_or4_retardada USE ENTITY WORK.or4(logicaretard);
FOR DUT13: inversor_retardat USE ENTITY WORK.inversor(logicaretard);

FOR DUT14: la_porta_xor2 USE ENTITY WORK.xor2(logica);
FOR DUT15: la_porta_xor2_retardada USE ENTITY WORK.xor2(logicaretard);

BEGIN

DUT0: inversor PORT MAP (ent1,sortida_inversor);

DUT1: la_porta_and2 PORT MAP (ent1,ent2,sortida_and2);
DUT2: la_porta_and3 PORT MAP (ent1,ent2,ent3,sortida_and3);
DUT3: la_porta_and4 PORT MAP (ent1,ent2,ent3,ent4,sortida_and4);
DUT4: la_porta_or2 PORT MAP (ent1,ent2,sortida_or2);
DUT5: la_porta_or3 PORT MAP (ent1,ent2,ent3,sortida_or3);
DUT6: la_porta_or4 PORT MAP (ent1,ent2,ent3,ent4,sortida_or4);

DUT7: la_porta_and2_retardada PORT MAP (ent1,ent2,sortida_ret_and2);
DUT8: la_porta_and3_retardada PORT MAP (ent1,ent2,ent3,sortida_ret_and3);
DUT9: la_porta_and4_retardada PORT MAP (ent1,ent2,ent3,ent4,sortida_ret_and4);
DUT10: la_porta_or2_retardada PORT MAP (ent1,ent2, sortida_ret_or2);
DUT11: la_porta_or3_retardada PORT MAP (ent1,ent2,ent3,sortida_ret_or3);
DUT12: la_porta_or4_retardada PORT MAP (ent1,ent2,ent3,ent4,sortida_ret_or4);
DUT13: inversor_retardat PORT MAP (ent1,sortida_ret_inversor);
DUT14: la_porta_xor2 PORT MAP (ent1,ent2, sortida_xor2);
DUT15: la_porta_xor2_retardada PORT MAP (ent1,ent2,sortida_ret_xor2);

PROCESS (ent1,ent2,ent3,ent4)
BEGIN
ent1 <= NOT ent1 AFTER 50 ns;
ent2 <= NOT ent2 AFTER 100 ns;
ent3 <= NOT ent3 AFTER 200 ns;
ent4 <= NOT ent4 AFTER 400 ns;
END PROCESS;
END test;

--En el interval [500,549) es prenen els valors ent1=0, ent2=1, ent3=0 i ent4=1, i els valors de sortida de les portes són:
--AND2: Com els valors són 0,1 dona 0.
--AND3: Com els valors són 0,1,0 dona 0.
--AND4: Com els valors són 0,1,0,1 dona 0.
--OR2: Com els valors són 0,1 dona 1.
--OR3: Com els valors són 0,1,0 dona 1.
--OR4: Com els valors són 0,1,0,1 dona 1.
--XOR2: Com els valors també són 0,1 dona 1.
--Inversor: Com el valor és 0, dona 1.
--Inversor retardat: Primer dona 0 i després canvia a 1.
