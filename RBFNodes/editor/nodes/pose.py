# <pep8 compliant>

import bpy

from . import node
from ... import language
from ... core import poses, rbf, utils


# Get the current language.
strings = language.getLanguage()


class SkipCallback(object):
    """Class for preventing a button callback for the edit mode.
    """
    def __init__(self):
        self.state = False


skip = SkipCallback()


class RBFPoseNode(node.RBFNode):
    """Pose node.
    """
    bl_idname = "RBFPoseNode"
    bl_label = strings.POSE_LABEL
    bl_icon = 'ARMATURE_DATA'

    # ------------------------------------------------------------------
    # Property callbacks
    # ------------------------------------------------------------------

    def toggleEditPose(self, context):
        """Callback for toggling the edit pose checkbox.
        Enabling puts the current pose into edit mode, disabling stores
        the adjusted pose values.

        :param context: The current context.
        :type context: bpy.context
        """
        if self.edit_pose:
            if not poses.editMode.state:
                result = poses.editPose(context, self)
                if result:
                    poses.editMode.state = True
                # If entering edit mode is not possible toggle the
                # checkbox state back.
                else:
                    skip.state = True
                    self.edit_pose = False
            # If another pose is already in edit mode toggle the
            # checkbox state back.
            else:
                skip.state = True
                self.edit_pose = False
        else:
            if not skip.state:
                rbf.update(context)
                poses.editMode.state = False
            skip.state = False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    edit_pose : bpy.props.BoolProperty(name="Editing",
                                       description=strings.ANN_EDIT_POSE,
                                       update=toggleEditPose)

    poseIndex : bpy.props.IntProperty()
    driverData : bpy.props.StringProperty(name="Driver Data")
    drivenData : bpy.props.StringProperty(name="Driven Data")
    driverSize : bpy.props.IntProperty()
    drivenSize : bpy.props.IntProperty()

    version : bpy.props.StringProperty()

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addOutput("RBFPoseSocket", strings.POSE_LABEL)
        utils.setVersion(self)

    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        if not self.edit_pose:
            row0 = layout.row(align=True)
            row0.operator("rbfnodes.recall_and_edit_pose").nodeName = self.name
        row1 = layout.row(align=True)
        row1.prop(self, "edit_pose",
                  text=("Stop Editing" if self.edit_pose else "Start Edit (No Recall)"),
                  toggle=True)
        row1.separator(factor=1.0)
        row1.operator("rbfnodes.recall_pose").nodeName = self.name
        row2 = layout.row(align=True)
        row2.prop(self, "driverData")
        row3 = layout.row(align=True)
        row3.prop(self, "drivenData")
        layout.row(align=True).label(text=
                                     "Driver Size = " + str(self.driverSize) +
                                     ", Driven Size = " + str(self.drivenSize) +
                                     ", Pose Index = " + str(self.poseIndex))

    def draw_buttons_ext(self, context, layout):
        """Draw node buttons in the sidebar.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        self.draw(context, layout)
