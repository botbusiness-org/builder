import time
from typing import Annotated
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from loguru import logger
from sqlalchemy.orm.attributes import flag_modified

from langflow.api.utils import DbSession
from langflow.api.v1.endpoints import simple_run_flow
from langflow.api.v1.schemas import SimplifiedAPIRequest
from langflow.helpers.flow import get_flow_by_id_or_endpoint_name
from langflow.services.database.models.flow import Flow
from langflow.services.database.models.flow.utils import get_all_website_input_components_in_flow
from langflow.services.deps import get_telemetry_service
from langflow.services.telemetry.schema import RunPayload

website_router = APIRouter(tags=["Website Router"])


async def _update_page_store(
    db_session: DbSession,
    flow: Flow,
    page_path: str,
    content: str,
):
    """Update the flow's page store with the new content for the given page path."""
    try:
        db_flow = await db_session.get(Flow, flow.id)
        if not db_flow:
            raise HTTPException(status_code=404, detail="Flow not found")

        website_components = get_all_website_input_components_in_flow(db_flow.data)
        modified = False
        for component in website_components:
            template = component["data"]["node"]["template"]
            use_store = template.get("use_store", {}).get("value", False)
            if use_store:
                store = template.get("page_store", {}).get("value", [])
                for page in store:
                    if page["path"] == page_path:
                        page["content"] = content
                        break
                else:
                    store.append({"path": page_path, "content": content})
                template["page_store"]["value"] = store
                modified = True
                break

        if modified:
            flag_modified(db_flow, "data")
            db_session.add(db_flow)
            await db_session.flush()
            await db_session.commit()
            await db_session.refresh(db_flow)
            logger.debug(f"Updated page store for flow {flow.id}: {page_path}")
    except Exception as exc:
        logger.error(f"Failed to update page store in flow {flow.id}: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@website_router.get("/website/{flow_id_or_name}", response_class=HTMLResponse)
async def redirect_to_trailing_slash(request: Request):
    path = request.url.path
    if not path.endswith("/"):
        path += "/"
    query = f"?{request.url.query}" if request.url.query else ""
    html = f"""
    <html>
      <head>
        <meta http-equiv="refresh" content="0; url={path}{query}">
        <script>window.location.replace("{path}{query}");</script>
      </head>
      <body>
        <p>Redirecting to <a href="{path}{query}">{path}{query}</a> ...</p>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@website_router.api_route(
    "/website/{flow_id_or_name}/{page_path:path}", methods=["GET", "POST"], response_class=HTMLResponse
)
async def serve_website(
    flow: Annotated[Flow, Depends(get_flow_by_id_or_endpoint_name)],
    request: Request,
    background_tasks: BackgroundTasks,
    db_session: DbSession,
    page_path: str = "",
):
    telemetry_service = get_telemetry_service()
    start_time = time.perf_counter()
    page_path = "/" + page_path if not page_path.startswith("/") else page_path

    logger.debug(f"Received website request: flow={flow.id}, path={page_path}")
    error_msg = ""

    if flow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")

    try:
        try:
            data = dict(request.query_params) if request.method == "GET" else await request.json()
        except Exception as exc:
            error_msg = str(exc)
            raise HTTPException(status_code=500, detail=error_msg) from exc

        try:
            website_components = get_all_website_input_components_in_flow(flow.data)
            tweaks = {}
            require_link = False
            allowed_paths = set("/")

            if not website_components:
                raise HTTPException(status_code=500, detail="Add a Website Input component to serve a website")

            for component in website_components:
                tweaks[component["id"]] = {"data": data, "path": page_path}
                template = component["data"]["node"]["template"]
                use_store = template.get("use_store", {}).get("value", False)
                require_link = require_link or (use_store and template.get("require_link", {}).get("value", False))

                if use_store:
                    store = template.get("page_store", {}).get("value", [])
                    for page in store:
                        if page["path"] == page_path:
                            return HTMLResponse(page["content"])
                        if require_link:
                            base_path = page["path"] if page["path"].endswith("/") else page["path"] + "/"
                            content = page["content"]
                            soup = BeautifulSoup(content, "html.parser")
                            internal_links = [
                                urljoin(base_path, link.get("href"))
                                for link in soup.find_all("a", href=True)
                                if not link.get("href").startswith(("http://", "https://"))
                            ]
                            allowed_paths.update(internal_links)

            if require_link and page_path not in allowed_paths:
                logger.debug(f"Path {page_path} not in allowed paths: {allowed_paths}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

            input_request = SimplifiedAPIRequest(
                input_value="",
                input_type="website",
                output_type="website",
                tweaks=tweaks,
                session_id=None,
            )

            result = await simple_run_flow(
                flow=flow,
                input_request=input_request,
            )
        except Exception as exc:
            error_msg = str(exc)
            raise HTTPException(status_code=500, detail=error_msg) from exc
    finally:
        background_tasks.add_task(
            telemetry_service.log_package_run,
            RunPayload(
                run_is_website=True,
                run_seconds=int(time.perf_counter() - start_time),
                run_success=not error_msg,
                run_error_message=error_msg,
            ),
        )

    if not result or not result.outputs:
        raise HTTPException(status_code=500, detail="No result returned from the flow")

    html = None
    for outputs in result.outputs:
        for output in outputs.outputs:
            if not output or output.component_display_name != "Website Output":
                continue
            html = output.results["html"].get_text()

    if not html:
        raise HTTPException(status_code=500, detail="No HTML output returned from the flow")

    background_tasks.add_task(
        _update_page_store,
        db_session=db_session,
        flow=flow,
        page_path=page_path,
        content=html,
    )

    return HTMLResponse(content=html)
