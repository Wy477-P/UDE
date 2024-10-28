using System.IO;
using System.Threading.Tasks;
using System.Runtime.InteropServices;
using IniParser;
using IniParser.Model;
using System.Text.Json;
using System.Collections.Generic;
using System.Windows.Forms;
using System.Threading;
using System.Net.Http;
using RGiesecke.DllExport;


namespace ApiCallerLibrary
{
    public class ApiCaller
    {
        public class Config
        {
            public string api_key { get; set; }
            public string gemini_model { get; set; }
            public string system_instructions { get; set; }
            public float temperature { get; set; }
            public float top_p { get; set; }
            public int top_k { get; set; }
        }

        private static void CopyToClipboard(string textToCopy)
        {
            if (textToCopy == null) return;
            
            Thread thread = new Thread(() =>
            {
                
                Thread.CurrentThread.SetApartmentState(ApartmentState.STA);
                Clipboard.SetText(textToCopy);
            });

            
            thread.Start();
            thread.Join();
        }

        private static string CopyFromClipboard()
        {
            string clipboardText = "";


            Thread thread = new Thread(() =>
            {
                
                Thread.CurrentThread.SetApartmentState(ApartmentState.STA);
                clipboardText = Clipboard.GetText();
            });
            
            thread.Start();
            thread.Join();
            return clipboardText;
        }





        // Main Method (UDG)
        [DllExport("CallApi", CallingConvention = CallingConvention.StdCall)]
        public static async Task<string> CallApi(
            string configPath,
            string gcontextjson,
            string goutput)
        {

            string userInput = CopyFromClipboard();
            var parser = new FileIniDataParser();
            IniData data = parser.ReadFile(configPath);

            Config config = new Config
            {
                api_key = data["UDG"]["api_key"],
                gemini_model = data["UDG"]["gemini_model"],
                system_instructions = data["UDG"]["system_instructions"],
                temperature = float.Parse(data["UDG"]["temperature"]),
                top_p = float.Parse(data["UDG"]["top_p"]),
                top_k = int.Parse(data["UDG"]["top_k"])
            };

            // Update Context (User Portion)
            ac(userInput, gcontextjson, "user");

            // Load Context
            List<Dictionary<string, object>> con;
            using (StreamReader r = new StreamReader(gcontextjson))
            {
                string json = r.ReadToEnd();
                con = JsonSerializer.Deserialize<List<Dictionary<string, object>>>(json);
            }


            // SN
            var SN = new Dictionary<string, object>
            {
                { "system_instruction", new Dictionary<string, object>
                    {
                        { "parts", new List<Dictionary<string, string>>
                            {
                    new Dictionary<string, string> { { "text", config.system_instructions } }
                            }
                        }
                    }
                },
                { "safetySettings", new List<Dictionary<string, string>>
                    {
                        new Dictionary<string, string> { { "category", "HARM_CATEGORY_HARASSMENT" }, { "threshold", "BLOCK_NONE" } },
                        new Dictionary<string, string> { { "category", "HARM_CATEGORY_HATE_SPEECH" }, { "threshold", "BLOCK_NONE" } },
                        new Dictionary<string, string> { { "category", "HARM_CATEGORY_SEXUALLY_EXPLICIT" }, { "threshold", "BLOCK_NONE" } },
                        new Dictionary<string, string> { { "category", "HARM_CATEGORY_DANGEROUS_CONTENT" }, { "threshold", "BLOCK_NONE" } }
                    }
                },
                { "generationConfig", new Dictionary<string, object>
                    {
                        { "temperature", config.temperature },
                        { "topP", config.top_p },
                        { "topK", config.top_k }
                    }
                },
                { "contents", con }
            };

            using (var client = new HttpClient())
            {
                client.DefaultRequestHeaders.Add("Content-Type", "application/json");

                var url = $"https://generativelanguage.googleapis.com/v1beta/models/{config.gemini_model}:generateContent?key={config.api_key}";
                var content = new StringContent(JsonSerializer.Serialize(SN), System.Text.Encoding.UTF8, "application/json");

                var response = await client.PostAsync(url, content);
                var RP_string = await response.Content.ReadAsStringAsync();
            
                File.WriteAllText(goutput, RP_string);
            }
            string OP = ""; // Initialize OP to an empty string

            using (StreamReader r = new StreamReader(goutput))
            {
                string json = r.ReadToEnd();
                var RP = JsonSerializer.Deserialize<Dictionary<string, object>>(json);

                if (RP.TryGetValue("candidates", out var candidates) && candidates is List<object> candidatesList && candidatesList.Count > 0)
                {
                    var firstCandidate = candidatesList[0] as Dictionary<string, object>;
                    if (firstCandidate != null && firstCandidate.TryGetValue("content", out var content) && content is Dictionary<string, object> contentDict)
                    {
                        if (contentDict.TryGetValue("parts", out var parts) && parts is List<object> partsList && partsList.Count > 0)
                        {
                            var firstPart = partsList[0] as Dictionary<string, object>;
                            if (firstPart != null && firstPart.TryGetValue("text", out var text) && text is string textString)
                            {
                                OP = textString;
                            }
                        }
                    }
                }
            }
            ac(OP, gcontextjson, "model");
            return OP;
        }
        // Update Context (AC)
        private static void ac(string userInput, string gcontextjson, string role)
        {
            List<Dictionary<string, object>> con;

            // Check if the file exists
            if (File.Exists(gcontextjson))
            {
                // Read the existing context from the JSON file
                con = JsonSerializer.Deserialize<List<Dictionary<string, object>>>(File.ReadAllText(gcontextjson));
            }
            else
            {
                // Create the file with a blank JSON array
                using (var file = File.Create(gcontextjson))
                {
                    using (var writer = new StreamWriter(file))
                    {
                        writer.WriteLine("[]"); // Initialize with a blank array
                    }
                }
                con = new List<Dictionary<string, object>>(); // Initialize to an empty list
            }

            // Create the new entry
            var entry = new Dictionary<string, object>
            {
                { "role", role }, // Use the role parameter
                { "parts", new List<Dictionary<string, string>> { new Dictionary<string, string> { { "text", userInput } } } }
            };

            // Append the entry to the context
            con.Add(entry);

            // Write the updated context back to the JSON file
            File.WriteAllText(gcontextjson, JsonSerializer.Serialize(con));
        }

        [DllExport("ClearContext", CallingConvention = CallingConvention.StdCall)]
        public static void ClearContext(string gcontextjson)
        {
            // Create the file with a blank JSON array
            using (var file = File.Create(gcontextjson))
            {
                using (var writer = new StreamWriter(file))
                {
                    writer.WriteLine("[]"); // Initialize with a blank array
                }
            }
        }
    }
}
