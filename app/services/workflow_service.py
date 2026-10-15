import uuid
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.workflow import WorkflowInstance, WorkflowTransition


def create_workflow_instance(
    db: Session,
    tenant_id: uuid.UUID,
    entity_type: str,
    entity_id: uuid.UUID,
    submitted_by: uuid.UUID,
    status: str = "SUBMITTED",
    current_step: str = "HOD_APPROVAL"
) -> WorkflowInstance:
    """Initializes or updates a workflow instance and its transition record."""
    existing = db.query(WorkflowInstance).filter(
        WorkflowInstance.tenant_id == tenant_id,
        WorkflowInstance.entity_type == entity_type,
        WorkflowInstance.entity_id == entity_id
    ).first()

    if existing:
        existing.status = status
        existing.current_step = current_step
        existing.submitted_by = submitted_by
        existing.submitted_at = datetime.now(timezone.utc)
        existing.completed_at = None
        instance = existing
    else:
        instance = WorkflowInstance(
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            submitted_by=submitted_by,
            status=status,
            current_step=current_step,
            submitted_at=datetime.now(timezone.utc)
        )
        db.add(instance)
    db.flush()

    transition = WorkflowTransition(
        tenant_id=tenant_id,
        instance_id=instance.id,
        from_status="DRAFT",
        to_status=status,
        actor_id=submitted_by,
        remarks="Workflow initiated",
        occurred_at=datetime.now(timezone.utc)
    )
    db.add(transition)
    db.flush()
    return instance


def transition_workflow(
    db: Session,
    instance: WorkflowInstance,
    to_status: str,
    actor_id: uuid.UUID,
    remarks: Optional[str] = None,
    new_step: Optional[str] = None
) -> WorkflowTransition:
    """Records a state change on an active workflow instance."""
    from_status = instance.status
    instance.status = to_status
    if new_step:
        instance.current_step = new_step
    if to_status in ["APPROVED", "REJECTED", "COMPLETED"]:
        instance.completed_at = datetime.now(timezone.utc)

    transition = WorkflowTransition(
        tenant_id=instance.tenant_id,
        instance_id=instance.id,
        from_status=from_status,
        to_status=to_status,
        actor_id=actor_id,
        remarks=remarks,
        occurred_at=datetime.now(timezone.utc)
    )
    db.add(transition)
    db.flush()
    return transition
