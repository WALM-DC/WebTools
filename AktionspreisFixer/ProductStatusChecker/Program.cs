namespace ProductStatusChecker;
using ProductStatusChecker.Models;
using ProductStatusChecker.Services;
using ProductStatusChecker.Utils;

public class Program
{
    public static async Task Main(string[] args)
    {
        Console.WriteLine("=== ProductStatusChecker ===");

        string searchPath = @"C:\xxxlutz\IG-Creator\XXXLutz\ICOM";
        string outputFile = @"F:\WebTools\public\listCS.json";

        if (!Directory.Exists(searchPath))
        {
            Console.WriteLine("ERROR: ICOM folder not found: " + searchPath);
            return;
        }

        Console.WriteLine("Scanning models...");
        var (models, apiTasks) = ModelScanner.FindAllJson(searchPath);

        Console.WriteLine($"Models found: {models.Count}");
        Console.WriteLine($"API tasks: {apiTasks.Count}");

        Console.WriteLine("Running API requests...");
        var results = await ProductConfigClient.FetchAll(apiTasks);

        Console.WriteLine($"API responses: {results.Count}");

        Console.WriteLine("Merging results...");
        ApiTaskBuilder.MergeApiResults(models, results);

        Console.WriteLine("Saving JSON output...");
        JsonWriter.SaveJsonFile(models, outputFile);

        Console.WriteLine("DONE.");
    }
}
