#region Help:  Introduction to the Script Component
/* The Script Component allows you to perform virtually any operation that can be accomplished in
 * a .Net application within the context of an Integration Services data flow.
 *
 * Expand the other regions which have "Help" prefixes for examples of specific ways to use
 * Integration Services features within this script component. */
#endregion
#region Namespaces
using System.IO;
using Microsoft.SqlServer.Dts.Runtime.Wrapper;
using System.Data.OleDb;
#endregion
/// <summary>
/// This is the class to which to add your code.  Do not change the name, attributes, or parent
/// of this class.
/// </summary>
[Microsoft.SqlServer.Dts.Pipeline.SSISScriptComponentEntryPointAttribute]
public class ScriptMain : UserComponent
{
    #region Help:  Using Integration Services variables and parameters
    /* To use a variable in this script, first ensure that the variable has been added to
     * either the list contained in the ReadOnlyVariables property or the list contained in
     * the ReadWriteVariables property of this script component, according to whether or not your
     * code needs to write into the variable.  To do so, save this script, close this instance of
     * Visual Studio, and update the ReadOnlyVariables and ReadWriteVariables properties in the
     * Script Transformation Editor window.
     * To use a parameter in this script, follow the same steps. Parameters are always read-only.
     *
     * Example of reading from a variable or parameter:
     *  DateTime startTime = Variables.MyStartTime;
     *
     * Example of writing to a variable:
     *  Variables.myStringVariable = "new value";
     */
    #endregion
    #region Help:  Using Integration Services Connnection Managers
    /* Some types of connection managers can be used in this script component.  See the help topic
     * "Working with Connection Managers Programatically" for details.
     *
     * To use a connection manager in this script, first ensure that the connection manager has
     * been added to either the list of connection managers on the Connection Managers page of the
     * script component editor.  To add the connection manager, save this script, close this instance of
     * Visual Studio, and add the Connection Manager to the list.
     *
     * If the component needs to hold a connection open while processing rows, override the
     * AcquireConnections and ReleaseConnections methods.
     * 
     * Example of using an ADO.Net connection manager to acquire a SqlConnection:
     *  object rawConnection = Connections.SalesDB.AcquireConnection(transaction);
     *  SqlConnection salesDBConn = (SqlConnection)rawConnection;
     *
     * Example of using a File connection manager to acquire a file path:
     *  object rawConnection = Connections.Prices_zip.AcquireConnection(transaction);
     *  string filePath = (string)rawConnection;
     *
     * Example of releasing a connection manager:
     *  Connections.SalesDB.ReleaseConnection(rawConnection);
     */
    #endregion
    #region Help:  Firing Integration Services Events
    /* This script component can fire events.
     *
     * Example of firing an error event:
     *  ComponentMetaData.FireError(10, "Process Values", "Bad value", "", 0, out cancel);
     *
     * Example of firing an information event:
     *  ComponentMetaData.FireInformation(10, "Process Values", "Processing has started", "", 0, fireAgain);
     *
     * Example of firing a warning event:
     *  ComponentMetaData.FireWarning(10, "Process Values", "No rows were received", "", 0);
     */
    #endregion
    IDTSConnectionManager100 connMgr;
    OleDbConnection conn;
    OleDbDataReader reader;
    public override void AcquireConnections(object Transaction)
    {
        connMgr = this.Connections.Connection;
        conn = (OleDbConnection)connMgr.AcquireConnection(null);
    }
    /// <summary>
    /// This method is called once, before rows begin to be processed in the data flow.
    ///
    /// You can remove this method if you don't need to do anything here.
    /// </summary>
    public override void PreExecute()
    {
        /// string sql = "SELECT top (10) DatesPivot_SubmittedToClosingDate, 'ihInformation(ExtraData,Subsidy_Amount)' AS SubsidyAmount FROM pclinfo";
        string path = @"c:\PCLender\PCL_Update\pcl_update.sql";
        string sql = File.ReadAllText(path);
        OleDbCommand cmd = new OleDbCommand(sql, conn);
        reader = cmd.ExecuteReader();
    }
    /// <summary>
    /// This method is called after all the rows have passed through this component.
    ///
    /// You can delete this method if you don't need to do anything here.
    /// </summary>
    public override void PostExecute()
    {
        reader.Close();
    }
    public override void ReleaseConnections()
    {
        connMgr.ReleaseConnection(conn);
    }
    public override void CreateNewOutputRows()
    {
        while (reader.Read())
        {
            {
                Output0Buffer.AddRow();
                Output0Buffer.LoanOfficerEmail = reader["LoanOfficerEmail"].ToString();
                Output0Buffer.loanNumberId = reader["loan_Number_Id"].ToString();
            }
        }
    }
}



#region Help:  Introduction to the Script Component
/* The Script Component allows you to perform virtually any operation that can be accomplished in
 * a .Net application within the context of an Integration Services data flow.
 *
 * Expand the other regions which have "Help" prefixes for examples of specific ways to use
 * Integration Services features within this script component. */
#endregion

#region Namespaces
using System.IO;
using Microsoft.SqlServer.Dts.Runtime.Wrapper;
using System.Data.OleDb;
using System;

#endregion

/// <summary>
/// This is the class to which to add your code.  Do not change the name, attributes, or parent
/// of this class.
/// </summary>
[Microsoft.SqlServer.Dts.Pipeline.SSISScriptComponentEntryPointAttribute]
public class ScriptMain : UserComponent
{
    #region Help:  Using Integration Services variables and parameters
    /* To use a variable in this script, first ensure that the variable has been added to
     * either the list contained in the ReadOnlyVariables property or the list contained in
     * the ReadWriteVariables property of this script component, according to whether or not your
     * code needs to write into the variable.  To do so, save this script, close this instance of
     * Visual Studio, and update the ReadOnlyVariables and ReadWriteVariables properties in the
     * Script Transformation Editor window.
     * To use a parameter in this script, follow the same steps. Parameters are always read-only.
     *
     * Example of reading from a variable or parameter:
     *  DateTime startTime = Variables.MyStartTime;
     *
     * Example of writing to a variable:
     *  Variables.myStringVariable = "new value";
     */
    #endregion

    #region Help:  Using Integration Services Connnection Managers
    /* Some types of connection managers can be used in this script component.  See the help topic
     * "Working with Connection Managers Programatically" for details.
     *
     * To use a connection manager in this script, first ensure that the connection manager has
     * been added to either the list of connection managers on the Connection Managers page of the
     * script component editor.  To add the connection manager, save this script, close this instance of
     * Visual Studio, and add the Connection Manager to the list.
     *
     * If the component needs to hold a connection open while processing rows, override the
     * AcquireConnections and ReleaseConnections methods.
     * 
     * Example of using an ADO.Net connection manager to acquire a SqlConnection:
     *  object rawConnection = Connections.SalesDB.AcquireConnection(transaction);
     *  SqlConnection salesDBConn = (SqlConnection)rawConnection;
     *
     * Example of using a File connection manager to acquire a file path:
     *  object rawConnection = Connections.Prices_zip.AcquireConnection(transaction);
     *  string filePath = (string)rawConnection;
     *
     * Example of releasing a connection manager:
     *  Connections.SalesDB.ReleaseConnection(rawConnection);
     */
    #endregion

    #region Help:  Firing Integration Services Events
    /* This script component can fire events.
     *
     * Example of firing an error event:
     *  ComponentMetaData.FireError(10, "Process Values", "Bad value", "", 0, out cancel);
     *
     * Example of firing an information event:
     *  ComponentMetaData.FireInformation(10, "Process Values", "Processing has started", "", 0, fireAgain);
     *
     * Example of firing a warning event:
     *  ComponentMetaData.FireWarning(10, "Process Values", "No rows were received", "", 0);
     */
    #endregion

    IDTSConnectionManager100 connMgr;
    OleDbConnection conn;
    OleDbDataReader reader;

    public override void AcquireConnections(object Transaction)
    {
        connMgr = this.Connections.Connection;
        conn = (OleDbConnection)connMgr.AcquireConnection(null);
    }

    /// <summary>
    /// This method is called once, before rows begin to be processed in the data flow.
    /// </summary>
    public override void PreExecute()
    {
        // Show all column names and data types using DataView
        ShowDataPreview();

        // Set up reader for data processing
        string path = @"c:\PCLender\PCL_Update\pcl_update.sql";
        string sql = File.ReadAllText(path);
        OleDbCommand cmd = new OleDbCommand(sql, conn);
        reader = cmd.ExecuteReader();
    }


    /// <summary>
    /// NEW METHOD: Preview the data structure and sample rows
    /// </summary>
    private void ShowDataPreview()
    {
        try
        {
            bool fireAgain = true;
            string path = @"c:\PCLender\PCL_Update\pcl_update.sql";
            string sql = File.ReadAllText(path);
            
            using (OleDbCommand cmd = new OleDbCommand(sql, conn))
            {
                #pragma warning disable CA2100 // SQL from trusted file, not user input
                using (OleDbDataReader previewReader = cmd.ExecuteReader())
                #pragma warning restore CA2100
                {
                    ComponentMetaData.FireInformation(0, "DATA PREVIEW", "=== COLUMN STRUCTURE ===", "", 0, ref fireAgain);
                    
                    // Show all columns with their types
                    for (int i = 0; i < previewReader.FieldCount; i++)
                    {
                        string columnInfo = $"Column {i:D2}: {previewReader.GetName(i)} ({previewReader.GetFieldType(i).Name})";
                        ComponentMetaData.FireInformation(0, "Column Info", columnInfo, "", 0, ref fireAgain);
                    }
                    
                    ComponentMetaData.FireInformation(0, "DATA PREVIEW", "=== SAMPLE DATA (First 3 Rows) ===", "", 0, ref fireAgain);
                    
                    // Show first 3 rows of actual data
                    int rowNum = 0;
                    while (previewReader.Read() && rowNum < 3)
                    {
                        ComponentMetaData.FireInformation(0, "Row Data", $"--- ROW {rowNum + 1} ---", "", 0, ref fireAgain);
                        for (int i = 0; i < previewReader.FieldCount; i++)
                        {
                            string value = previewReader[i]?.ToString() ?? "NULL";
                            // Truncate long values for readability
                            if (value.Length > 50)
                                value = value.Substring(0, 47) + "...";
                            string rowData = $"  {previewReader.GetName(i)}: {value}";
                            ComponentMetaData.FireInformation(0, "Field Data", rowData, "", 0, ref fireAgain);
                        }
                        rowNum++;
                    }
                    
                    ComponentMetaData.FireInformation(0, "SUMMARY", $"Found {previewReader.FieldCount} total columns", "", 0, ref fireAgain);
                }
            }
        }
        catch (System.Exception ex)
        {
            bool cancel = false;
            ComponentMetaData.FireError(0, "ShowDataPreview", $"ERROR: {ex.Message}", "", 0, out cancel);
        }
    }
    /// <summary>
    /// This method is called after all the rows have passed through this component.
    ///
    /// You can delete this method if you don't need to do anything here.
    /// </summary>
    public override void PostExecute()
    {
        reader.Close();
    }
    /// <summary>

    public override void ReleaseConnections()
    {
        connMgr.ReleaseConnection(conn);
    }
    public override void CreateNewOutputRows()
    {
        while (reader.Read())
        {
            Output0Buffer.AddRow();

            // Existing columns
            Output0Buffer.LoanOfficerEmail = reader["LoanOfficerEmail"].ToString();
            Output0Buffer.loanNumberId = reader["loan_Number_Id"].ToString();

            // NEW: 10 Additional Columns (ALL AS STRINGS)
            Output0Buffer.DatesPivotSubmittedToClosingDate = reader["DatesPivot_SubmittedToClosingDate"].ToString();
            Output0Buffer.LoanSentPrefunding = reader["LoanSentPrefunding"].ToString();
            Output0Buffer.LenderCreditFeeLine = reader["LenderCreditFeeLine"].ToString();
            Output0Buffer.SubsidyAmount = reader["SubsidyAmount"].ToString();
            Output0Buffer.LenderCureAmount = reader["LenderCureAmount"].ToString();
            Output0Buffer.BorrowerEmail = reader["BorrowerEmail"].ToString();
            Output0Buffer.ProcessorEmail = reader["ProcessorEmail"].ToString();
            Output0Buffer.AccountExecutiveName = reader["AccountExecutiveName"].ToString();
            Output0Buffer.DatesPivotApplicationDate = reader["DatesPivot_ApplicationDate"].ToString();
            Output0Buffer.AppraisalOrderedDate = reader["AppraisalOrderedDate"].ToString();


        }
    }
}



#region Help:  Introduction to the Script Component
/* The Script Component allows you to perform virtually any operation that can be accomplished in
 * a .Net application within the context of an Integration Services data flow.
 *
 * Expand the other regions which have "Help" prefixes for examples of specific ways to use
 * Integration Services features within this script component. */
#endregion

#region Namespaces
using System.IO;
using Microsoft.SqlServer.Dts.Runtime.Wrapper;
using System.Data.OleDb;
using System;
using System.Reflection;  // Add this line
using System.Collections.Generic;
#endregion

/// <summary>
/// This is the class to which to add your code.  Do not change the name, attributes, or parent
/// of this class.
/// </summary>
[Microsoft.SqlServer.Dts.Pipeline.SSISScriptComponentEntryPointAttribute]
public class ScriptMain : UserComponent
{
    #region Help:  Using Integration Services variables and parameters
    /* To use a variable in this script, first ensure that the variable has been added to
     * either the list contained in the ReadOnlyVariables property or the list contained in
     * the ReadWriteVariables property of this script component, according to whether or not your
     * code needs to write into the variable.  To do so, save this script, close this instance of
     * Visual Studio, and update the ReadOnlyVariables and ReadWriteVariables properties in the
     * Script Transformation Editor window.
     * To use a parameter in this script, follow the same steps. Parameters are always read-only.
     *
     * Example of reading from a variable or parameter:
     *  DateTime startTime = Variables.MyStartTime;
     *
     * Example of writing to a variable:
     *  Variables.myStringVariable = "new value";
     */
    #endregion

    #region Help:  Using Integration Services Connnection Managers
    /* Some types of connection managers can be used in this script component.  See the help topic
     * "Working with Connection Managers Programatically" for details.
     *
     * To use a connection manager in this script, first ensure that the connection manager has
     * been added to either the list of connection managers on the Connection Managers page of the
     * script component editor.  To add the connection manager, save this script, close this instance of
     * Visual Studio, and add the Connection Manager to the list.
     *
     * If the component needs to hold a connection open while processing rows, override the
     * AcquireConnections and ReleaseConnections methods.
     * 
     * Example of using an ADO.Net connection manager to acquire a SqlConnection:
     *  object rawConnection = Connections.SalesDB.AcquireConnection(transaction);
     *  SqlConnection salesDBConn = (SqlConnection)rawConnection;
     *
     * Example of using a File connection manager to acquire a file path:
     *  object rawConnection = Connections.Prices_zip.AcquireConnection(transaction);
     *  string filePath = (string)rawConnection;
     *
     * Example of releasing a connection manager:
     *  Connections.SalesDB.ReleaseConnection(rawConnection);
     */
    #endregion

    #region Help:  Firing Integration Services Events
    /* This script component can fire events.
     *
     * Example of firing an error event:
     *  ComponentMetaData.FireError(10, "Process Values", "Bad value", "", 0, out cancel);
     *
     * Example of firing an information event:
     *  ComponentMetaData.FireInformation(10, "Process Values", "Processing has started", "", 0, fireAgain);
     *
     * Example of firing a warning event:
     *  ComponentMetaData.FireWarning(10, "Process Values", "No rows were received", "", 0);
     */
    #endregion

    IDTSConnectionManager100 connMgr;
    OleDbConnection conn;
    OleDbDataReader reader;

    public override void AcquireConnections(object Transaction)
    {
        connMgr = this.Connections.Connection;
        conn = (OleDbConnection)connMgr.AcquireConnection(null);
    }

    /// <summary>
    /// This method is called once, before rows begin to be processed in the data flow.
    /// </summary>
    public override void PreExecute()
    {
        // Show all column names and data types using DataView
        ShowDataPreview();

        // Set up reader for data processing
        string path = @"c:\PCLender\PCL_Update\pcl_update.sql";
        string sql = File.ReadAllText(path);
        OleDbCommand cmd = new OleDbCommand(sql, conn);
        reader = cmd.ExecuteReader();
    }


    /// <summary>
    /// NEW METHOD: Preview the data structure and sample rows
    /// </summary>
    private void ShowDataPreview()
    {
        try
        {
            bool fireAgain = true;
            string path = @"c:\PCLender\PCL_Update\pcl_update.sql";
            string sql = File.ReadAllText(path);

            using (OleDbCommand cmd = new OleDbCommand(sql, conn))
            {
                #pragma warning disable CA2100 // SQL from trusted file, not user input
                using (OleDbDataReader previewReader = cmd.ExecuteReader())
                #pragma warning restore CA2100
                {
                    ComponentMetaData.FireInformation(0, "DATA PREVIEW", "=== COLUMN STRUCTURE ===", "", 0, ref fireAgain);

                    // Show all columns with their types
                    for (int i = 0; i < previewReader.FieldCount; i++)
                    {
                        string columnInfo = $"Column {i:D2}: {previewReader.GetName(i)} ({previewReader.GetFieldType(i).Name})";
                        ComponentMetaData.FireInformation(0, "Column Info", columnInfo, "", 0, ref fireAgain);
                    }

                    ComponentMetaData.FireInformation(0, "DATA PREVIEW", "=== SAMPLE DATA (First 3 Rows) ===", "", 0, ref fireAgain);

                    // Show first 3 rows of actual data
                    int rowNum = 0;
                    while (previewReader.Read() && rowNum < 3)
                    {
                        ComponentMetaData.FireInformation(0, "Row Data", $"--- ROW {rowNum + 1} ---", "", 0, ref fireAgain);
                        for (int i = 0; i < previewReader.FieldCount; i++)
                        {
                            string value = previewReader[i]?.ToString() ?? "NULL";
                            // Truncate long values for readability
                            if (value.Length > 50)
                                value = value.Substring(0, 47) + "...";
                            string rowData = $"  {previewReader.GetName(i)}: {value}";
                            ComponentMetaData.FireInformation(0, "Field Data", rowData, "", 0, ref fireAgain);
                        }
                        rowNum++;
                    }

                    ComponentMetaData.FireInformation(0, "SUMMARY", $"Found {previewReader.FieldCount} total columns", "", 0, ref fireAgain);
                }
            }
        }
        catch (System.Exception ex)
        {
            bool cancel = false;
            ComponentMetaData.FireError(0, "ShowDataPreview", $"ERROR: {ex.Message}", "", 0, out cancel);
        }
    }
    /// <summary>
    /// This method is called after all the rows have passed through this component.
    ///
    /// You can delete this method if you don't need to do anything here.
    /// </summary>
    public override void PostExecute()
    {
        reader.Close();
    }
    /// <summary>

    public override void ReleaseConnections()
    {
        connMgr.ReleaseConnection(conn);
    }

    public override void CreateNewOutputRows()
    {
        // Debug: Show all available output properties ONCE
        var bufferType = Output0Buffer.GetType();
        var allProperties = bufferType.GetProperties()
            .Where(p => p.Name != "Item" && p.Name != "IsEndOfRowset" && !p.Name.StartsWith("DirectRow"))
            .OrderBy(p => p.Name)
            .ToArray();

        bool fireAgain = true;
        ComponentMetaData.FireInformation(0, "DEBUG", "=== Available Output Properties ===", "", 0, ref fireAgain);
        foreach (var prop in allProperties)
        {
            ComponentMetaData.FireInformation(0, "DEBUG", $"Property: {prop.Name} (Type: {prop.PropertyType.Name})", "", 0, ref fireAgain);
        }
        ComponentMetaData.FireInformation(0, "DEBUG", "=== End Output Properties ===", "", 0, ref fireAgain);

        while (reader.Read())
        {
            Output0Buffer.AddRow();

            // Process exactly the first 10 columns
            int maxColumns = Math.Min(10, reader.FieldCount);
            
            for (int i = 0; i < maxColumns; i++)
            {
                string columnName = reader.GetName(i);
                string columnValue = reader[i]?.ToString() ?? "";

                // Debug: Show what we're trying to map
                ComponentMetaData.FireInformation(0, "DEBUG",
                    $"Column {i}: DB='{columnName}' Value='{(columnValue.Length > 15 ? columnValue.Substring(0, 15) + "..." : columnValue)}'", "", 0, ref fireAgain);

                // Use reflection to set properties dynamically
                var property = bufferType.GetProperty(columnName);

                if (property != null && property.CanWrite)
                {
                    try
                    {
                        // Convert all values to strings for simplicity
                        property.SetValue(Output0Buffer, columnValue, null);
                        ComponentMetaData.FireInformation(0, "DEBUG",
                            $"✓ Mapped: {columnName} → {property.PropertyType.Name}", "", 0, ref fireAgain);
                    }
                    catch (Exception ex)
                    {
                        ComponentMetaData.FireWarning(0, "Column Mapping",
                            $"❌ Error setting '{columnName}': {ex.Message}", "", 0);
                    }
                }
                else
                {
                    if (property == null)
                    {
                        ComponentMetaData.FireWarning(0, "Column Mapping",
                            $"❌ Property '{columnName}' not found in output buffer", "", 0);
                        ComponentMetaData.FireInformation(0, "ACTION_NEEDED",
                            $"⚠️  ADD COLUMN: '{columnName}' as String in SSIS Script Component Output", "", 0, ref fireAgain);
                    }
                    else if (!property.CanWrite)
                    {
                        ComponentMetaData.FireWarning(0, "Column Mapping",
                            $"❌ Property '{columnName}' is read-only", "", 0);
                    }
                }
            }
        }
    }
}