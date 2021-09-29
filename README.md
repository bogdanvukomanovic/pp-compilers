# Programski prevodioci - Projekat


![architecture](https://user-images.githubusercontent.com/47822683/135255124-9925909c-3590-4e0c-9530-4c9c05eb4c08.png)


Cilj projektnog zadatka je individualno implementirati interpreter i generator koda za Pascal programski jezik. Potrebno je generisati kod u C programskom jeziku koji ne sme sadržati sintaksne greške. Projekat se sastoji iz dve faze. Prva faza podrazumeva generisanje apstraktnog sintaksnog stabla, dok je druga faza posvećena implementaciji interpretera i generatora koda.

## [Prva faza] Potrebno je podržati sledeće celine:

- Promenljive i tipovi podataka (integer, real, boolean, char, string)
- Binarne i unarne aritmetičke operacije (+, -, *, /, div, mod)
- Binarne i unarne logičke operacije (not, and, or, xor)
- Relacione operacije (=, <>, <, <=, >, >=)
- If-Else naredba
- Repeat-Until naredba sa instrukcijama za kontrolu toka (break, continue)
- While-Do naredba sa instrukcijama za kontrolu toka (break, continue)
- For-Do naredba sa instrukcijama za kontrolu toka (to, downto, break, continue)
- Funkcije za rad sa brojevima (inc, dec, ord, chr)
- Funkcije za rad sa stringovima (length, insert)
- Funkcije za rad sa konzolom (read, write, readln, writeln)
- Korišćenje nizova primitivih tipova podataka
- Korisnički definisane funkcije i procedure (function, procedure, exit)

## [Druga faza] Potrebno je podržati sledeće celine:
- Interpreter Pascal koda - potrebno je podržati sve celine iz prve faze
- Generator C koda - potrebno je podržati sve celine iz prve faze
- Prijavljivanje grešaka:
  - Sintaksne greške pronađene leksičkom analizom izvornog koda
  - Korišćenje nedeklarisane promenljive
  - Korišćenje nekompatibilnih tipova
  - Detektovanje beskonačne rekurzije

