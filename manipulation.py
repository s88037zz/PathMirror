import RLPy
from random import randrange

def local_to_world_translate(obj, local_pos):
    transform = obj.WorldTransform()
    transform_matrix = transform.Matrix()
    transform_matrix.SetTranslate(RLPy.RVector3.ZERO)

    local_matrix = RLPy.RMatrix4()
    local_matrix.MakeIdentity()
    local_matrix.SetTranslate(local_pos)

    # Get world-space position by multiplying local-space with the transform-space
    world_matrix = local_matrix * transform_matrix

    return world_matrix.GetTranslate()


def local_move(obj, local_pos):
    """
    move object in local-space
    :param obj: RObject
    :param local_pos: RVector3
    :return: Bool
    """
    world_position = local_to_world_translate(obj, local_pos)
    current_time = RLPy.RGlobal.GetTime()

    # Set positional keys
    t_control = obj.GetControl("Transform")
    t_data_block = t_control.GetDataBlock()
    t_data_block.SetData("Position/PositionX", current_time, RLPy.RVariant(world_position.x))
    t_data_block.SetData("Position/PositionY", current_time, RLPy.RVariant(world_position.y))
    t_data_block.SetData("Position/PositionZ", current_time, RLPy.RVariant(world_position.z))

    # Force update iClone native UI
    RLPy.RGlobal.SetTime(RLPy.RGlobal.GetTime() + RLPy.RTime(1))
    RLPy.RGlobal.SetTime(RLPy.RGlobal.GetTime() - RLPy.RTime(1))


def get_bounding_box(obj):
    maxPoint = RLPy.RVector3()
    cenPoint = RLPy.RVector3()
    minPoint = RLPy.RVector3()

    status = obj.GetBounds(maxPoint, cenPoint, minPoint)
    bounding = maxPoint - cenPoint  # Can also be: cenPoint - minPoint
    return bounding