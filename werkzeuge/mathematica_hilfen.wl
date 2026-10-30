(* Gemeinsame Bausteine für die Übungsnotebooks (task/solved aus einer Quelle).
   Wird von mathematica_<thema>.wl mit Get geladen. *)

kursordner = FileNameJoin[{DirectoryName[$InputFileName], ".."}];
nbziel = FileNameJoin[{kursordner, "mathematica"}];

(* Eingabezelle aus Quelltext: hübsch formatiert (2D-Brüche, Potenzen usw.). Einige Befehle bleiben aber als Text
   stehen, damit man sie wiedererkennt und abtippen kann: D[...] und Integrate[...] (nicht ∂ und ∫), Reals (nicht ℝ)
   und Graphics/Graphics3D (sonst würde die Eingabezelle schon eine fertige Grafik enthalten, z. B. aus Red und einem
   noch unbekannten Punkt, und Mathematica meldet „Red is not a Graphics3D primitive or directive“). *)
alsText = {D -> befehlD, Integrate -> befehlIntegrate, Reals -> befehlReals,
           Graphics -> befehlGraphics, Graphics3D -> befehlGraphics3D, MatrixForm -> befehlMatrixForm};
boxen[s_String] := (ToExpression[s, InputForm, HoldComplete] /. alsText /.
      HoldComplete[e_] :> MakeBoxes[e, StandardForm]) /.
    Thread[ToString /@ Values[alsText] -> ToString /@ Keys[alsText]];
(* Nachgestelltes „// Befehl“ (MatrixForm, N, Simplify, Expand …) bleibt so stehen, wie es geschrieben ist.
   Sonst wird z. B. aus „Ksys // MatrixForm“ eine unsichtbare Hülle, und in der Zelle steht nur „Ksys“. *)
(* nur an „ // “ außerhalb aller Klammern trennen (in Table[… // MatrixForm, …] bleibt es Teil des Ausdrucks) *)
tiefe[s_String] := StringCount[s, "[" | "{" | "("] - StringCount[s, "]" | "}" | ")"];
obenTrennen[s_String] := Module[{pos = Select[StringPosition[s, " // "], tiefe[StringTake[s, #[[1]] - 1]] == 0 &]},
   StringTake[s, #] & /@ Partition[Flatten[{1, Riffle[pos[[All, 1]] - 1, pos[[All, 2]] + 1], StringLength[s]}], 2]];
postfix[s_String] := With[{teile = obenTrennen[s]},
   Fold[RowBox[{#1, "//", #2}] &, boxen[First[teile]], Rest[teile]]];
(* Bei einer Zuweisung „x = … // f“ gehört das // zur rechten Seite (x = f[…]), wie Mathematica es liest. *)
ein[s_String] := Cell[BoxData[
    If[StringMatchQ[s, RegularExpression["\\s*[A-Za-z][A-Za-z0-9]*\\s*=[^=].*"]] && Length[obenTrennen[s]] > 1,
      With[{t = StringSplit[s, "=", 2]}, RowBox[{StringTrim[t[[1]]], "=", postfix[StringTrim[t[[2]]]]}]],
      postfix[s]]], "Input"];
(* Kurze Erklärung zu einem Rechenschritt, direkt unter der Eingabezelle (nur in der Musterlösung) *)
erklaerung[s_String] := Cell[s, "Text", FontColor -> GrayLevel[0.35], CellMargins -> {{66, 10}, {10, 2}}];
leer[hinweis_String] := Cell[BoxData[RowBox[{"(*", " ", hinweis, " ", "*)"}]], "Input"];
txt[s_String] := Cell[s, "Text"];
(* Aufgabenstellung: Einleitung, darunter die Teilaufgaben a), b), ... je in einer eigenen Zeile *)
aufgabe[einleitung_String, teile_List] := txt[StringRiffle[Prepend[teile, einleitung], "\n"]];
(* Grafik aus dem Kurs (SVG wird über rsvg-convert als PNG eingebettet) *)
bild[svg_String, breite_:500] := Module[{png = FileNameJoin[{$TemporaryDirectory, "kursbild.png"}]},
  Run["rsvg-convert -z 2 -b white -o '" <> png <> "' '" <> FileNameJoin[{kursordner, svg}] <> "'"];
  Cell[BoxData[ToBoxes[Image[Import[png], ImageSize -> breite]]], "Text"]];

(* Aufgabenschritt: {Überschrift, Erklärung, {Code ...}, Hinweis für die Aufgabe}
   Jeder Code-Eintrag ist ein String oder {Code, Erklärung}; die Erklärung steht nur in der Musterlösung,
   kurz und für Anfänger:innen in Mathematica verständlich (was macht der Befehl, warum dieser Schritt). *)
codeText[c_String] := c;
codeText[{c_String, _String}] := c;
codeZellen[c_String] := {ein[c]};
codeZellen[{c_String, e_String}] := {ein[c], erklaerung[e]};
schrittzellen[s_List, geloest_] := Join[
  {Cell[s[[1]], "Subsection"]},
  If[s[[2]] =!= "", {txt[s[[2]]]}, {}],
  If[geloest, Flatten[codeZellen /@ s[[3]]], {txt["Gesucht: " <> s[[4]]], leer["Ihre Eingabe"]}]];

speichereNB[name_String, zellen_List] := Module[{pfad = FileNameJoin[{nbziel, name}]},
  Export[pfad, Notebook[zellen, StyleDefinitions -> "Default.nb", Magnification :> 1.25 Inherited], "NB"];
  Print["geschrieben: ", pfad]];

(* Lösungscode im Kernel ausführen und Ergebnisse ausgeben (Kontrolle) *)
pruefeCode[code_List] := Do[With[{c = codeText[cc]}, With[{r = ToExpression[c]},
    If[!StringEndsQ[c, ";"] && FreeQ[r, Graphics | Graphics3D | Legended | Image],
      Print[c, "  =>  ", ToString[r /. m_MatrixForm :> First[m], InputForm]]]]], {cc, code}];
