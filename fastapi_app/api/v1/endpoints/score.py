from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import asyncio
from schemas.transaction import TransactionInput, BulkTransactionInput
from schemas.prediction import PredictionResponse, DetailedPredictionResponse
from services.scoring import FraudScoringService
from core.security import verify_api_key
from core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Initialize scoring service
scoring_service = FraudScoringService()

@router.post(
    "/score",
    response_model=PredictionResponse,
    summary="Score single transaction",
    description="Analyze a single transaction and return fraud score"
)
async def score_transaction(
    transaction: TransactionInput,
    api_key: str = Depends(verify_api_key)
):
    """
    Score a single transaction for fraud detection.
    
    Returns fraud score (0-1), risk level, and recommendation.
    """
    try:
        result = scoring_service.score_transaction(transaction.dict())
        return PredictionResponse(**result)
    except Exception as e:
        logger.error(f"Error scoring transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to score transaction: {str(e)}"
        )

@router.post(
    "/score/detailed",
    response_model=DetailedPredictionResponse,
    summary="Score with explanation",
    description="Score transaction with feature importance and explanations"
)
async def score_transaction_detailed(
    transaction: TransactionInput,
    api_key: str = Depends(verify_api_key)
):
    """
    Score transaction with detailed explanation.
    
    Includes feature importance, triggered rules, and model confidence.
    """
    try:
        result = scoring_service.score_transaction_detailed(transaction.dict())
        return DetailedPredictionResponse(**result)
    except Exception as e:
        logger.error(f"Error in detailed scoring: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to score transaction: {str(e)}"
        )

@router.post(
    "/score/batch",
    summary="Batch score transactions",
    description="Score multiple transactions in a single request"
)
async def score_transactions_batch(
    batch: BulkTransactionInput,
    api_key: str = Depends(verify_api_key)
):
    """
    Score multiple transactions in batch.
    
    Maximum 100 transactions per request.
    """
    try:
        results = []
        
        for txn in batch.transactions:
            try:
                result = scoring_service.score_transaction(txn.dict())
                results.append({
                    'user_id': txn.user_id,
                    'amount': txn.amount,
                    'success': True,
                    'prediction': result
                })
            except Exception as e:
                logger.error(f"Error scoring transaction for user {txn.user_id}: {str(e)}")
                results.append({
                    'user_id': txn.user_id,
                    'amount': txn.amount,
                    'success': False,
                    'error': str(e)
                })
        
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        return {
            'total': len(results),
            'successful': successful,
            'failed': failed,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Error in batch scoring: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch scoring failed: {str(e)}"
        )

@router.post(
    "/score/async",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Async transaction scoring",
    description="Submit transaction for asynchronous processing"
)
async def score_transaction_async(
    transaction: TransactionInput,
    api_key: str = Depends(verify_api_key)
):
    """
    Submit transaction for asynchronous scoring.
    
    Returns task ID for tracking (if Celery is configured).
    """
    try:
        # For now, process synchronously
        # In production, integrate with Celery
        result = scoring_service.score_transaction(transaction.dict())
        
        return {
            'status': 'processing',
            'message': 'Transaction submitted for scoring',
            'result': result
        }
        
    except Exception as e:
        logger.error(f"Error in async scoring: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit transaction: {str(e)}"
        )
