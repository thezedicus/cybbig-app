// Cybbig — rapport JSON d'analyse headless Ghidra.
// Exécuté par analyzeHeadless via -postScript. Argument 0 = chemin du fichier JSON de sortie.
// Pur exportateur : aucune heuristique de risque ici (faite côté backend Python).
//@category Cybbig
//@keybinding
//@menupath
//@toolbar
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;
import ghidra.program.model.symbol.SymbolTable;

import java.io.FileWriter;
import java.util.ArrayList;
import java.util.List;

public class ReaHeadlessReport extends GhidraScript {

    // Sortie ASCII pure : tout caractère hors [0x20..0x7e] est échappé en \\uXXXX,
    // ce qui rend le JSON indépendant de l'encodage de FileWriter (lu en UTF-8 côté Python).
    private static String esc(String s) {
        if (s == null) {
            return "";
        }
        StringBuilder b = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"':
                    b.append("\\\"");
                    break;
                case '\\':
                    b.append("\\\\");
                    break;
                case '\n':
                    b.append("\\n");
                    break;
                case '\r':
                    b.append("\\r");
                    break;
                case '\t':
                    b.append("\\t");
                    break;
                default:
                    if (c < 0x20 || c > 0x7e) {
                        b.append(String.format("\\u%04x", (int) c));
                    } else {
                        b.append(c);
                    }
            }
        }
        return b.toString();
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String out = (args.length > 0 && args[0] != null && !args[0].isEmpty())
                ? args[0] : "rea_report.json";

        final int maxFns = 400;
        final int maxImports = 1500;
        final int maxExports = 500;
        final int maxStrings = 800;
        final int maxDecompiled = 12;

        StringBuilder sb = new StringBuilder();
        sb.append("{");

        // --- Métadonnées du programme ---
        sb.append("\"program\":{");
        sb.append("\"name\":\"").append(esc(currentProgram.getName())).append("\",");
        sb.append("\"format\":\"").append(esc(currentProgram.getExecutableFormat())).append("\",");
        sb.append("\"language\":\"").append(esc(currentProgram.getLanguageID().getIdAsString())).append("\",");
        sb.append("\"compiler\":\"").append(esc(currentProgram.getCompilerSpec().getCompilerSpecID().getIdAsString())).append("\",");
        sb.append("\"image_base\":\"").append(esc(String.valueOf(currentProgram.getImageBase()))).append("\",");
        sb.append("\"min_address\":\"").append(esc(currentProgram.getMinAddress() == null ? "" : currentProgram.getMinAddress().toString())).append("\",");
        sb.append("\"max_address\":\"").append(esc(currentProgram.getMaxAddress() == null ? "" : currentProgram.getMaxAddress().toString())).append("\",");
        sb.append("\"md5\":\"").append(esc(currentProgram.getExecutableMD5())).append("\",");
        sb.append("\"sha256\":\"").append(esc(currentProgram.getExecutableSHA256())).append("\"");
        sb.append("},");

        // --- Fonctions ---
        int fnCount = 0;
        List<String> fnJson = new ArrayList<>();
        FunctionIterator fit = currentProgram.getFunctionManager().getFunctions(true);
        while (fit.hasNext()) {
            if (monitor.isCancelled()) {
                break;
            }
            Function f = fit.next();
            fnCount++;
            if (fnJson.size() < maxFns) {
                long size = 0;
                try {
                    size = f.getBody().getNumAddresses();
                } catch (Exception e) {
                    size = 0;
                }
                fnJson.add("{\"name\":\"" + esc(f.getName())
                        + "\",\"entry\":\"" + esc(f.getEntryPoint().toString())
                        + "\",\"size\":" + size
                        + ",\"external\":" + f.isExternal()
                        + ",\"thunk\":" + f.isThunk() + "}");
            }
        }
        sb.append("\"function_count\":").append(fnCount).append(",");
        sb.append("\"functions\":[").append(String.join(",", fnJson)).append("],");

        // Décompilation ciblée et bornée pour donner du contexte au triage sans
        // faire exploser la durée ou la taille du rapport sur les gros binaires.
        DecompInterface decompiler = new DecompInterface();
        List<String> decompiledJson = new ArrayList<>();
        int decompiledCount = 0;
        try {
            if (decompiler.openProgram(currentProgram)) {
                FunctionIterator dit = currentProgram.getFunctionManager().getFunctions(true);
                while (dit.hasNext() && decompiledCount < maxDecompiled && !monitor.isCancelled()) {
                    Function f = dit.next();
                    if (f.isExternal() || f.isThunk()) continue;
                    DecompileResults result = decompiler.decompileFunction(f, 5, monitor);
                    if (result == null || !result.decompileCompleted() || result.getDecompiledFunction() == null) continue;
                    String code = result.getDecompiledFunction().getC();
                    if (code == null || code.isEmpty()) continue;
                    if (code.length() > 2500) code = code.substring(0, 2500);
                    decompiledJson.add("{\"name\":\"" + esc(f.getName())
                            + "\",\"entry\":\"" + esc(f.getEntryPoint().toString())
                            + "\",\"code\":\"" + esc(code) + "\"}");
                    decompiledCount++;
                }
            }
        } finally {
            decompiler.dispose();
        }
        sb.append("\"decompiled_count\":").append(decompiledCount).append(",");
        sb.append("\"decompiled_functions\":[").append(String.join(",", decompiledJson)).append("],");

        // --- Imports (symboles externes) ---
        SymbolTable st = currentProgram.getSymbolTable();
        int impCount = 0;
        List<String> impJson = new ArrayList<>();
        SymbolIterator eit = st.getExternalSymbols();
        while (eit.hasNext()) {
            if (monitor.isCancelled()) {
                break;
            }
            Symbol s = eit.next();
            impCount++;
            if (impJson.size() < maxImports) {
                String lib = "";
                try {
                    lib = s.getParentNamespace() != null ? s.getParentNamespace().getName() : "";
                } catch (Exception e) {
                    lib = "";
                }
                impJson.add("{\"name\":\"" + esc(s.getName())
                        + "\",\"library\":\"" + esc(lib) + "\"}");
            }
        }
        sb.append("\"import_count\":").append(impCount).append(",");
        sb.append("\"imports\":[").append(String.join(",", impJson)).append("],");

        // --- Exports / points d'entrée externes ---
        int expCount = 0;
        List<String> expJson = new ArrayList<>();
        AddressIterator epit = st.getExternalEntryPointIterator();
        while (epit.hasNext()) {
            if (monitor.isCancelled()) {
                break;
            }
            Address a = epit.next();
            expCount++;
            if (expJson.size() < maxExports) {
                Symbol s = st.getPrimarySymbol(a);
                String nm = s != null ? s.getName() : "";
                expJson.add("{\"name\":\"" + esc(nm)
                        + "\",\"address\":\"" + esc(a.toString()) + "\"}");
            }
        }
        sb.append("\"export_count\":").append(expCount).append(",");
        sb.append("\"exports\":[").append(String.join(",", expJson)).append("],");

        // --- Chaînes définies ---
        // On parcourt les données définies et on ne retient que celles dont la
        // valeur est une chaîne (API stable, indépendante de la version Ghidra).
        int strCount = 0;
        List<String> strJson = new ArrayList<>();
        DataIterator di = currentProgram.getListing().getDefinedData(true);
        while (di.hasNext()) {
            if (monitor.isCancelled()) {
                break;
            }
            Data d = di.next();
            Object v;
            try {
                v = d.getValue();
            } catch (Exception e) {
                v = null;
            }
            if (!(v instanceof String)) {
                continue;
            }
            strCount++;
            if (strJson.size() < maxStrings) {
                String sv = (String) v;
                if (sv.length() > 400) {
                    sv = sv.substring(0, 400);
                }
                strJson.add("{\"addr\":\"" + esc(d.getAddress().toString())
                        + "\",\"value\":\"" + esc(sv) + "\"}");
            }
        }
        sb.append("\"string_count\":").append(strCount).append(",");
        sb.append("\"strings\":[").append(String.join(",", strJson)).append("]");

        sb.append("}");

        try (FileWriter w = new FileWriter(out)) {
            w.write(sb.toString());
        }
        println("Cybbig: rapport ecrit -> " + out
                + " (" + fnCount + " fonctions, " + impCount + " imports, "
                + expCount + " exports, " + strCount + " chaines)");
    }
}
