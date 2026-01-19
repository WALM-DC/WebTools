namespace ProductStatusChecker.Models;

public class VariantEntry
{
    public string VariantId { get; set; } = "";
    public string ProductNumber { get; set; } = "";
    public string Description { get; set; } = "";
    public bool Online { get; set; }
    public bool Konfig { get; set; }
    public string Error { get; set; } = "";
}

public class ModelEntry
{
    public string ModelId { get; set; } = "";
    public string FileName { get; set; } = "";
    public string ProductNumber { get; set; } = "";    // REQUIRED by Python
    public string ProductVariants { get; set; } = "";  // Python flat string
    public string VariantConfig { get; set; } = "";    // Python flat string
    public string VariantOnline { get; set; } = "";    // Python flat string
    public bool Online { get; set; }                   // Python flag
    public bool Konfig { get; set; }                   // Python flag

    public string ModelName { get; set; } = "";
    public string Locale { get; set; } = "";
    public string Currency { get; set; } = "";
    public string Catalog { get; set; } = "";
    public string Model { get; set; } = "";
    public string Brand { get; set; } = "";
    public string BrandName { get; set; } = "";
    public string ProductGroup { get; set; } = "";
    public string Description { get; set; } = "";
    public string Preis { get; set; } = "";
    public string Entlastung { get; set; } = ""; // note: Python bug uses this name
    public string Aktion { get; set; } = "";
    public object Pricing { get; set; } = new();
    public List<object>? Properties { get; set; }

    // For internal processing:
    public Dictionary<string, VariantEntry> Variants { get; set; }
        = new(StringComparer.OrdinalIgnoreCase);
}
