using System.IO;
using Aspose.Words;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Serilog;

namespace DocConverter
{
    class Program
    {
        static void Main(string[] args)
        {

            var services = new ServiceCollection();
            ConfigureServices(services);

            Log.Logger = new LoggerConfiguration()
                .WriteTo.Console(Serilog.Events.LogEventLevel.Information)
                .CreateLogger();

            var provider = services.BuildServiceProvider();

            var logger = provider.GetService<ILogger<Program>>();
            if (args.Length > 0)
            {
                string docPath = args[0];
                if (File.Exists(docPath))
                {


                    logger.LogInformation($"Converting Document {docPath}");
                    var doc = new Document(docPath);
                    string filename = Path.GetFileNameWithoutExtension(docPath) + ".docx";
                    string outputPath = Path.GetDirectoryName(docPath);

                    logger.LogInformation("Outputing DOCX file.");
                    doc.Save(Path.Join(outputPath, filename), SaveFormat.Docx);
                                        
                }
                else
                {
                    logger.LogInformation($"File {docPath} does not exist.");
                }
            }
            else
            {
                logger.LogInformation("DOC file path is required.");
            }
        }

        static void ConfigureServices(IServiceCollection services)
        {
            services.AddLogging(config => config.AddSerilog());

        }
    }

    
}
