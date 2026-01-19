namespace ProductStatusChecker.Models;

public class ConfigResult
{
    public string ModelId { get; set; } = "";
    public string VariantId { get; set; } = "";
    public string ProductNumber { get; set; } = "";

    public bool Online { get; set; }
    public bool Konfigurable { get; set; }
    public string Error { get; set; } = "";
}
