using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
using System.Text.Json;
using ProductStatusChecker.Models;
using ProductStatusChecker.Utils;

namespace ProductStatusChecker.Services;

public static class ProductConfigClient
{
    static readonly HttpClient http;

    static ProductConfigClient()
    {
        var h = new HttpClientHandler
        {
            ServerCertificateCustomValidationCallback =
                (_,_,_,_) => true
        };
        http = new HttpClient(h) { Timeout = TimeSpan.FromSeconds(10) };
    }

    public static async Task<ConfigResult> FetchSingle(ApiTask t)
    {
        try
        {
            int mandant = CountryRailMapper.CodeFromCountry(t.Locale);
            string rail = CountryRailMapper.CodeFromRail(t.Locale, t.Brand);

            string url =
                $"https://services.ist.lutz.gmbh/HybrisProductDelivery/clients/{mandant}/assortmentLines/{rail}/productNumbers/{t.ProductNumber}/{t.VariantId}";

            string txt = await http.GetStringAsync(url);

            // PYTHON LOGIC: TRY JSON
            JsonDocument doc;
            try
            {
                doc = JsonDocument.Parse(txt);
            }
            catch
            {
                // PYTHON: JSON PARSE FAIL = OFFLINE
                return new ConfigResult
                {
                    ModelId = t.ModelId,
                    VariantId = t.VariantId,
                    ProductNumber = t.ProductNumber,
                    Online = false,
                    Konfigurable = false,
                    Error = "non-json"
                };
            }

            var root = doc.RootElement;

            // PYTHON: If "Configuration" is missing → offline
            if (!root.TryGetProperty("Configuration", out var config))
            {
                return new ConfigResult
                {
                    ModelId = t.ModelId,
                    VariantId = t.VariantId,
                    ProductNumber = t.ProductNumber,
                    Online = false,
                    Konfigurable = false,
                    Error = ""
                };
            }

            // PYTHON: Config exists → ONLINE
            bool online = true;

            // PYTHON: ConfigId or SystemId → KONFIG_TRUE
            string cfgId = config.TryGetProperty("ConfigurationId", out var a) ? a.GetString() ?? "" : "";
            string sysId = config.TryGetProperty("ConfigurationSystemId", out var b) ? b.GetString() ?? "" : "";

            bool konfig = (cfgId.Length > 0 || sysId.Length > 0);

            return new ConfigResult
            {
                ModelId = t.ModelId,
                VariantId = t.VariantId,
                ProductNumber = t.ProductNumber,
                Online = online,
                Konfigurable = konfig,
                Error = ""
            };
        }
        catch (Exception ex)
        {
            // PYTHON: ANY ERROR = OFFLINE
            return new ConfigResult
            {
                ModelId = t.ModelId,
                VariantId = t.VariantId,
                ProductNumber = t.ProductNumber,
                Online = false,
                Konfigurable = false,
                Error = ex.Message
            };
        }
    }

    public static async Task<List<ConfigResult>> FetchAll(List<ApiTask> tasks)
    {
        var list = new List<Task<ConfigResult>>();
        foreach (var t in tasks) list.Add(FetchSingle(t));
        return (await Task.WhenAll(list)).ToList();
    }
}
