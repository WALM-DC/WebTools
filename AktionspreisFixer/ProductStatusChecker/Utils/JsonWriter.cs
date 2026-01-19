namespace ProductStatusChecker.Utils;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Unicode;
using ProductStatusChecker.Models;

public static class JsonWriter
{
    public static void SaveJsonFile(
        Dictionary<string, ModelEntry> modelList,
        string outputPath)
    {
        var options = new JsonSerializerOptions
        {
            WriteIndented = true,
            Encoder = JavaScriptEncoder.Create(UnicodeRanges.All),
            DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull
        };

        var json = JsonSerializer.Serialize(modelList, options);
        File.WriteAllText(outputPath, json);
    }
}
