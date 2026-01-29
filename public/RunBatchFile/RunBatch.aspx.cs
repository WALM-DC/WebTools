using System;
using System.Diagnostics;

namespace UpdateIndexProd.RunBatch
{
    public partial class RunBatch : System.Web.UI.Page
    {
        protected void Button1_Click(object sender, EventArgs e)
        {
            try
            {
                string batPath = @"D:\inetpub\wwwroot\idm\RunBatchFile\_GenerateIndexProd.bat";

                var psi = new ProcessStartInfo
                {
                    FileName = batPath,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (var process = Process.Start(psi))
                {
                    process.WaitForExit();
                }

                StatusLabel.Text = "Batch file executed.";
            }
            catch (Exception ex)
            {
                StatusLabel.Text = "Error: " + ex.Message;
            }
        }
    }
}