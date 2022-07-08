import tempfile
from typing import Union

import uvicorn
from fastapi import FastAPI, UploadFile, Query, File
from fastapi.responses import RedirectResponse

from portal_andino.update import catalog_restore
from portal_andino import info

app = FastAPI(
    title="API DatosAbiertos",
    description="""
    DatosAbiertos API te ayuda a hacer cosas asombrosas. 🚀

    ## Portal Andino

    En los portales podrás:

    * **Restaurar catálogos**.
    * **Verificar datasets** (_not implemented_).
    * ** ...
    """
)


@app.get("/")
def root():
    return RedirectResponse("/docs")


@app.get(
    "/portal/organizations",
    name="Organizaciones",
    description="Toma la url de un portal y devuelve su árbol de organizaciones."
)
def organizations_portal(
        url: str = Query(description="URL del portal")
):
    return info.get_organizations(url)


@app.post(
    "/portal/catalog/restore",
    name="Restauración de catálogo",
    description="Restaura los datasets de un catálogo original al portal pasado por parámetro. Si hay temas presentes "
                "en el DataJson que no están en el portal de CKAN, los genera."
)
async def catalog_restore(
        file: UploadFile = File(description="El catálogo de origen que se restaura."),
        origin_url: str = Query(description="La URL del portal CKAN de origen."),
        destination_url: str = Query(description="La URL del portal CKAN de destino."),
        apikey: str = Query(description="La apikey de un usuario con los permisos que le permitan crear o "
                                        "actualizar el dataset")
):
    with tempfile.NamedTemporaryFile() as catalog:
        content = await file.read()
        catalog.write(content)
        catalog.seek(0)
        pushed_datasets = catalog_restore(catalog.name, origin_url, destination_url, apikey)

    return pushed_datasets


@app.post(
    "/portal/catalog/is_valid",
    name="Valida Catálogo",
    description="Analiza la validez de la estructura de un catálogo"
)
async def is_valid_catalog(
        file: Union[UploadFile, None] = File(default=None, description="El catálogo a validar."),
        url: Union[str, None] = Query(default=None, description="La URL del portal que contiene el catalogo a validar.")
):
    if file:
        with tempfile.NamedTemporaryFile() as catalog:
            content = await file.read()
            catalog.write(content)
            catalog.seek(0)
            return info.is_valid_catalog(catalog.name)
    else:
        return info.is_valid_catalog(url)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
