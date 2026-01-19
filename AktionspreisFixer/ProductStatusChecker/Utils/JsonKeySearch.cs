namespace ProductStatusChecker.Utils;
using System.Text.Json;

public static class JsonKeySearch
{
    public static bool ContainsKey(JsonElement element, HashSet<string> targetKeys)
    {
        switch (element.ValueKind)
        {
            case JsonValueKind.Object:
                foreach (var prop in element.EnumerateObject())
                {
                    if (targetKeys.Contains(prop.Name))
                        return true;

                    if (ContainsKey(prop.Value, targetKeys))
                        return true;
                }
                break;

            case JsonValueKind.Array:
                foreach (var item in element.EnumerateArray())
                {
                    if (ContainsKey(item, targetKeys))
                        return true;
                }
                break;
        }

        return false;
    }
}
