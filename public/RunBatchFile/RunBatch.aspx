<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="RunBatch.aspx.cs" Inherits="UpdateIndexProd.RunBatch" %>

<!DOCTYPE html>
<html>
<head><title>Update Index Prod</title></head>
<body>
    <form id="form1" runat="server">
        <asp:Button ID="Button1" runat="server" Text="Run Batch File" OnClick="Button1_Click" />
        <asp:Label ID="StatusLabel" runat="server" Text="" />
    </form>
</body>
</html>