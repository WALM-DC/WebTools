namespace ProductStatusChecker.Utils;

public static class CountryRailMapper
{
    public static int CodeFromCountry(string country)
    {
        country = country.ToLowerInvariant();

        return country switch
        {
            "at" => 0,
            "si" => 2,
            "hr" => 3,
            "rs" => 6,
            "pl" => 9,
            "cz" => 10,
            "sk" => 11,
            "hu" => 12,
            "se" => 13,
            "ro" => 14,
            "ch" => 15,
            "de" => 17,
            _ => -1
        };
    }

    public static string CodeFromRail(string country, string rail)
    {
        country = country.ToLowerInvariant();
        rail = rail.ToLowerInvariant();

        return rail switch
        {
            "lu" => country == "de" ? "0Z" : "0L",
            "mm" => country == "hu" ? "0Y" : "0M",
            "mx" => (country == "cz" || country == "sk") ? "1X" : "0X",
            _ => "-1"
        };
    }
}
