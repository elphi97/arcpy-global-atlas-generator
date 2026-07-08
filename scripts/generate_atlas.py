import arcpy
import os

# 1. Path configuration
project_path = r"C:\LPA\Projects\arcpy-global-atlas-generator\atlas_template\atlas_template.aprx"
output_folder = r"C:\LPA\Projects\arcpy-global-atlas-generator\output"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 2. Project and object initialization

aprx = arcpy.mp.ArcGISProject(project_path)
layout = aprx.listLayouts("Layout")[0]
map_frame = layout.listElements("MAPFRAME_ELEMENT")[0]
title_text = layout.listElements("TEXT_ELEMENT","Text")[0]

# Countries layer path
map_obj = aprx.listMaps()[0]
coutries_layer = map_obj.listLayers("countries")[0]

# 3. Final PDF creations
final_pdf_path = os.path.join(output_folder, "Global_Atlas.pdf")
if os.path.exists(final_pdf_path):
    os.remove(final_pdf_path)
final_pdf = arcpy.mp.PDFDocumentCreate(final_pdf_path)

print("Atlas generation starting...")

# 4. Iterating through European countries
where_clause = "CONTINENT = 'Europe'"

with arcpy.da.SearchCursor(coutries_layer, ["SHAPE@", "NAME"], where_clause =where_clause) as cursor:
    for row in cursor:
        country_geom = row[0]
        country_name = row[1]

        print(f"Generating page for: {country_name}")
        
        #Country selection
        selection_query = f"NAME = '{country_name}'"

        #Selection specific country
        arcpy.management.SelectLayerByAttribute(coutries_layer, "NEW_SELECTION", selection_query)
        
        # Title name changing
        title_text.text = f"Map: {country_name}"

        #Zooming frame to specific country geometry
        map_frame.camera.setExtent(country_geom.extent)

        # Buffer with a slight zoom- out for better layer visibility
        map_frame.camera.scale = map_frame.camera.scale * 1.15

        # Exporting a  single page to a  temporary PDF
        temp_pdf = os.path.join(output_folder,f"temp_{country_name}.pdf")
        layout.exportToPDF(temp_pdf,resolution=150)

        # Adding page to main Atlas and deleting temporary file
        final_pdf.appendPages(temp_pdf)
        os.remove(temp_pdf)

#selection deleting
arcpy.management.SelectLayerByAttribute(coutries_layer, "CLEAR_SELECTION")
# 5. Saving and closing multipages PDF
final_pdf.saveAndClose()
print(f"Succes! Atlas was saved in : {final_pdf_path}")
        
