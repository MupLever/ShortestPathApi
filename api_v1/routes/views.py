from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from api_v1.routes import crud
from api_v1.routes.schemas import LegalAddress
from api_v1.routes.utils import graph_api, external_api

from configs.database import get_session_dependency


router = APIRouter(tags=["Routes"], prefix="/api/v1/shortest_path/routes")


@router.get("/", description="Список маршрутов")
async def get_routes(session: Session = Depends(get_session_dependency)):
    return crud.get_routes(session)


@router.get("/{route_id}/", description="Получить маршрут по идентификатору")
async def get_route(route_id: int, session: Session = Depends(get_session_dependency)):
    return crud.get_route(session, route_id)


@router.post("/", description="Добавить маршрут")
async def create_shortest_path(
    legal_addresses: List[LegalAddress],
    session: Session = Depends(get_session_dependency),
):
    coordinates_dict = external_api.get_coordinates(legal_addresses)

    edges_list = external_api.get_distances(coordinates_dict)

    data = graph_api.get_min_hamiltonian_cycle(edges_list)

    route = crud.create_route(session, data)
    msg = "SUCCESS: The shortest path has been successfully found"

    return {"message": msg, "shortest_path": route}


@router.delete("/{route_id}/", description="Удалить маршрут")
async def delete_route(
    route_id: int, session: Session = Depends(get_session_dependency)
):
    route = crud.get_route(session, route_id)

    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route with {route_id=} not found",
        )
    return crud.delete_route(session, route)


@router.put("/{route_id}/", description="Изменить маршрут")
async def update_route(
    route_id: int,
    legal_addresses: List[LegalAddress],
    session: Session = Depends(get_session_dependency),
):
    route = crud.get_route(session, route_id)

    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route with {route_id=} not found",
        )

    coordinates_dict = external_api.get_coordinates(legal_addresses)
    edges_list = external_api.get_distances(coordinates_dict)
    data = graph_api.get_min_hamiltonian_cycle(edges_list)

    new_route = crud.update_route(session, route, data)
    msg = "SUCCESS: The shortest path has been successfully found"

    return {"message": msg, "shortest_path": new_route}


# @router.patch("/{route_id}/")
# async def update_route(route_id: int, legal_addresses: List[LegalAddress]):
#     address_list = get_coordinates(legal_addresses)
#
#     data = get_distances(legal_addresses, address_list)
#
#     graph = HamiltonianGraph(data)
#     msg, data = graph.find_hamiltonian_cycle()
#     database[route_id] = data
#     return {"message": msg, "shortest_path": database[route_id]}
