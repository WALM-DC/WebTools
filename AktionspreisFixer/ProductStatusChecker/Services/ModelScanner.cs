using System.Text.Json;
using ProductStatusChecker.Models;
using ProductStatusChecker.Utils;

namespace ProductStatusChecker.Services;

public static class ModelScanner
{
    public static (Dictionary<string,ModelEntry>, List<ApiTask>) FindAllJson(string rootPath)
    {
        var models = new Dictionary<string,ModelEntry>(StringComparer.OrdinalIgnoreCase);
        var conds  = new Dictionary<string,JsonElement>(StringComparer.OrdinalIgnoreCase);

        foreach(var file in Directory.EnumerateFiles(rootPath, "*.json", SearchOption.AllDirectories))
        {

            string fn = Path.GetFileName(file);
            if (fn.Contains(" ") || fn.Equals("texts.json") || fn.Equals("catalog.json"))
                continue;

            string txt;
            try { txt = File.ReadAllText(file).TrimStart('\uFEFF'); }
            catch { continue; }

            JsonDocument doc;
            try { doc = JsonDocument.Parse(txt); }
            catch { continue; }

            var root = doc.RootElement;

            // ---------------- CONDITIONS.JSON ----------------
            if (fn.Equals("conditions.json", StringComparison.OrdinalIgnoreCase))
            {
                if (root.TryGetProperty("sets", out var sets))
                {
                    foreach (var entry in sets.EnumerateObject())
                        conds[entry.Name] = entry.Value.Clone();
                }
                continue;
            }

            // ---------------- MODEL.JSON ----------------
            if (!fn.Contains("@"))
                continue;

            if (!root.TryGetProperty("catalog", out var catalogProp))
                continue;

            string noExt = Path.GetFileNameWithoutExtension(fn);
            var parts = noExt.Split('@');
            if (parts.Length < 2)
                continue;

            string modelName = parts[0];
            string locale = parts[1];
            string catalog = catalogProp.ToString();
            string modelId = catalog.Split('.')[0] + "." + noExt;

            string Get(string k)=>root.TryGetProperty(k,out var v)?v.ToString():"";
            string GetSet(string k)=>root.TryGetProperty("settings",out var s)&&s.TryGetProperty(k,out var v)?v.ToString():"";
            object GetPricing()=>root.TryGetProperty("settings",out var s)&&s.TryGetProperty("pricing",out var p)
                                ? JsonSerializer.Deserialize<object>(p.GetRawText())!
                                : new object();
            var props=root.TryGetProperty("properties",out var pp)
                            ? JsonSerializer.Deserialize<List<object>>(pp.GetRawText())
                            : new List<object>();

            models[modelId] = new ModelEntry {
                ModelId = modelId,
                FileName = noExt,
                ModelName = modelName,
                Locale = locale,
                Catalog = catalog,
                Currency = Get("currency"),
                Model = Get("model"),
                Brand = Get("brand"),
                BrandName = Get("brandName"),
                ProductGroup = Get("productGroup"),
                Description = Get("description"),
                Preis = GetSet("kaa1"),
                Entlastung = GetSet("entlastung"),
                Aktion = GetSet("aktion"),
                Pricing = GetPricing(),
                Properties = props
            };

            if (fn.Equals("conditions.json", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("Found conditions.json: " + file);

                if (!root.TryGetProperty("sets", out var sets))
                {
                    Console.WriteLine("  ERROR: conditions.json has no 'sets' property!");
                    continue;
                }

                Console.WriteLine("  Sets keys:");
                foreach (var entry in sets.EnumerateObject())
                {
                    string key = entry.Name.Trim();  // <-- IMPORTANT
                    Console.WriteLine("    KEY: '" + key + "'");
                    conds[key] = entry.Value.Clone();
                }

                continue;
            }
        }

        // 🔥 This line was missing in your broken version
        return Merge(models, conds);
    }

    // ---------------- MERGE CONDITIONS → VARIANTS ----------------
    private static (Dictionary<string,ModelEntry>, List<ApiTask>) Merge(
        Dictionary<string,ModelEntry> models,
        Dictionary<string,JsonElement> conds)
    {
        var tasks = new List<ApiTask>();

        foreach (var (id, model) in models)
        {
            if (!conds.TryGetValue(model.FileName, out var variantGroup))
                continue;  // no matching conditions

            foreach (var variantObj in variantGroup.EnumerateObject())
            {
                string variantId = variantObj.Name;
                var v = variantObj.Value;

                if (!v.TryGetProperty("productNo", out var pnoProp))
                    continue;

                string productNo = pnoProp.ToString();
                string desc = v.TryGetProperty("description", out var d) ? d.ToString() : "";

                model.Variants[variantId] = new VariantEntry {
                    VariantId = variantId,
                    ProductNumber = productNo,
                    Description = desc
                };

                tasks.Add(new ApiTask {
                    ModelId = id,
                    Locale = model.Locale,
                    Brand = model.Brand,
                    ProductNumber = productNo,
                    VariantId = variantId
                });
            }
        }

        return (models, tasks);
    }
}
