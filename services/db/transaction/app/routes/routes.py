import logging
from fastapi import APIRouter, HTTPException, Request, Query
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse
)
from app.use_cases.create_transaction import CreateTransaction
from app.use_cases.update_transaction import UpdateTransaction
from app.use_cases.get_transaction import GetTransaction
from app.use_cases.delete_transaction import DeleteTransaction
from app.use_cases.search_transaction import SearchTransaction

logger = logging.getLogger(__name__)

def get_transaction_router(relational_db):
    router = APIRouter()

    @router.get("/", response_model=Dict[str, Any])
    def search_transactions(
        request: Request,
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0)
    ):
        """
        Paginated search for transactions.
        """
        filters = dict(request.query_params)
        filters.pop("limit", None)
        filters.pop("offset", None)
        logger.info(f"Searching transactions with filters={filters}, limit={limit}, offset={offset}")
        try:
            results, total = SearchTransaction(relational_db).execute(limit=limit, offset=offset, **filters)
            results = [TransactionResponse.model_validate(obj) for obj in results]
            logger.info(f"Found {len(results)} transactions (total={total})")
            return {
                "results": results,
                "limit": limit,
                "offset": offset,
                "total": total
            }
        except Exception as e:
            logger.exception(f"Exception during search for transactions: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during search")

    @router.get("/{item_id}", response_model=TransactionResponse)
    def get_transaction(item_id: UUID):
        logger.info(f"Fetching transaction with id={item_id}")
        result = GetTransaction(relational_db).execute(item_id)
        if result is None:
            logger.warning(f"Transaction with id={item_id} not found")
            raise HTTPException(status_code=404, detail="Transaction not found")
        return result

    @router.post("/", response_model=TransactionResponse)
    def create_transaction(payload: TransactionCreate):
        logger.info(f"Creating new transaction with payload={payload.dict()}")
        try:
            obj = CreateTransaction(relational_db).execute(payload)
            return obj
        except ValueError as e:
            logger.warning(f"HTTP error 400: {e} | Path: /")
            raise HTTPException(status_code=400, detail=str(e))
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                # Extract column name from error message for better user feedback
                error_msg = str(e.orig)
                if "Key (" in error_msg and ")=" in error_msg:
                    # Extract field name from "Key (field_name)=(value) already exists"
                    field_name = error_msg.split("Key (")[1].split(")=")[0]
                    field_value = error_msg.split(")=(")[1].split(") already exists")[0]
                    detail = f"The {field_name} '{field_value}' is already in use. Please choose a different value."
                else:
                    detail = "A unique constraint was violated. Please check your input values."
                logger.warning(f"Unique constraint violation during create: {detail}")
                raise HTTPException(status_code=400, detail=detail)
            logger.error(f"Integrity error during create: {str(e.orig)}")
            raise HTTPException(status_code=400, detail=str(e.orig).split("\n")[0])
        except Exception as e:
            logger.exception(f"Exception during create for transaction: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during create")

    @router.put("/{item_id}", response_model=TransactionResponse)
    def update_transaction(item_id: UUID, payload: TransactionUpdate):
        logger.info(f"Updating transaction with id={item_id}, payload={payload.dict(exclude_unset=True)}")
        try:
            updated = UpdateTransaction(relational_db).execute(item_id, payload)
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                # Extract column name from error message for better user feedback
                error_msg = str(e.orig)
                if "Key (" in error_msg and ")=" in error_msg:
                    # Extract field name from "Key (field_name)=(value) already exists"
                    field_name = error_msg.split("Key (")[1].split(")=")[0]
                    field_value = error_msg.split(")=(")[1].split(") already exists")[0]
                    detail = f"The {field_name} '{field_value}' is already in use. Please choose a different value."
                else:
                    detail = "A unique constraint was violated. Please check your input values."
                logger.warning(f"Unique constraint violation during update: {detail}")
                raise HTTPException(status_code=400, detail=detail)
            logger.error(f"Integrity error during update: {str(e.orig)}")
            raise HTTPException(status_code=400, detail=str(e.orig).split("\n")[0])
        except Exception as e:
            logger.exception(f"Exception during update for transaction with id={item_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during update")
        if updated is None:
            logger.warning(f"Update failed: transaction with id={item_id} not found")
            raise HTTPException(status_code=404, detail="Transaction not found")
        return updated

    @router.delete("/{item_id}")
    def delete_transaction(item_id: UUID):
        logger.info(f"Deleting transaction with id={item_id}")
        try:
            deleted = DeleteTransaction(relational_db).execute(item_id)
            if not deleted:
                logger.warning(f"Delete failed: transaction with id={item_id} not found")
                raise HTTPException(status_code=404, detail="Transaction not found")
            logger.info(f"Deleted transaction with id={item_id}")
            return {"detail": "Transaction deleted"}
        except Exception as e:
            logger.exception(f"Exception during delete for transaction with id={item_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during delete")

    return router
