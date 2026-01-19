namespace ProductStatusChecker.Services;
using ProductStatusChecker.Models;

public static class ApiTaskBuilder
{
    public static void MergeApiResults(Dictionary<string,ModelEntry> models, List<ConfigResult> results)
    {
        foreach (var r in results)
        {
            if (!models.TryGetValue(r.ModelId, out var model))
                continue;

            if (!model.Variants.TryGetValue(r.VariantId, out var variant))
                continue;

            variant.Online = r.Online;
            variant.Konfig = r.Konfigurable;
            variant.Error  = r.Error;
        }
    }
}
