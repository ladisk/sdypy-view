# -*- coding: utf-8 -*-
"""Functional tests for sdypy.view — Qt-free.

All functions under test are imported via the namespace package:
    from sdypy import view
"""

import importlib.util
import pytest
import numpy as np

from sdypy import view


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _quad_mesh():
    """Return a tiny 2-element quad mesh (4 nodes, 2 quads sharing an edge).

    Layout (z=0 plane):
        3---2---5
        |   |   |
        0---1---4

    nodes shape  : (6, 3)
    elements shape: (2, 4)  — quad elements (n_nodes_per_element = 4)
    """
    nodes = np.array(
        [
            [0.0, 0.0, 0.0],  # 0
            [1.0, 0.0, 0.0],  # 1
            [1.0, 1.0, 0.0],  # 2
            [0.0, 1.0, 0.0],  # 3
            [2.0, 0.0, 0.0],  # 4
            [2.0, 1.0, 0.0],  # 5
        ],
        dtype=float,
    )
    elements = np.array(
        [
            [0, 1, 2, 3],  # first quad
            [1, 4, 5, 2],  # second quad
        ],
        dtype=int,
    )
    return nodes, elements


def _tri_mesh():
    """Return a single triangle mesh (3 nodes, 1 tri element).

    nodes shape  : (3, 3)
    elements shape: (1, 3)
    """
    nodes = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.5, 1.0, 0.0],
        ],
        dtype=float,
    )
    elements = np.array([[0, 1, 2]], dtype=int)
    return nodes, elements


# ---------------------------------------------------------------------------
# 1.  create_fem_mesh
# ---------------------------------------------------------------------------

class TestCreateFemMesh:
    """Tests for view.create_fem_mesh(nodes, elements)."""

    def test_quad_mesh_n_points(self):
        """n_points of returned PolyData must equal the number of nodes."""
        nodes, elements = _quad_mesh()
        mesh = view.create_fem_mesh(nodes, elements)
        assert mesh.n_points == nodes.shape[0], (
            f"Expected {nodes.shape[0]} points, got {mesh.n_points}"
        )

    def test_quad_mesh_n_faces(self):
        """n_faces of returned PolyData must equal the number of elements.

        PyVista PolyData.n_cells can differ from the face count depending on
        how the mesh was built; n_faces (polygonal face count) is the reliable
        metric for FEM surfaces created via mesh.faces = ....
        """
        nodes, elements = _quad_mesh()
        mesh = view.create_fem_mesh(nodes, elements)
        assert mesh.n_faces == elements.shape[0], (
            f"Expected {elements.shape[0]} faces, got {mesh.n_faces}"
        )

    def test_tri_mesh_n_points_and_faces(self):
        """Works for triangular (3-node) elements as well."""
        nodes, elements = _tri_mesh()
        mesh = view.create_fem_mesh(nodes, elements)
        assert mesh.n_points == 3
        assert mesh.n_faces == 1

    def test_returns_pyvista_object(self):
        """Return type must be a PyVista PolyData (has .n_points attribute)."""
        nodes, elements = _quad_mesh()
        mesh = view.create_fem_mesh(nodes, elements)
        assert hasattr(mesh, "n_points")
        assert hasattr(mesh, "n_cells")


# ---------------------------------------------------------------------------
# 2.  prepare_animation_displacements
# ---------------------------------------------------------------------------

class TestPrepareAnimationDisplacements:
    """Tests for view.prepare_animation_displacements(data, n_nodes, n_frames)."""

    # -- 3-D input: (n_nodes, 3, n_frames) returned as-is -------------------

    def test_3d_input_passthrough_shape(self):
        """3-D input (n_nodes, 3, n_frames) is returned unchanged."""
        n_nodes, n_frames = 6, 20
        data = np.random.rand(n_nodes, 3, n_frames)
        result = view.prepare_animation_displacements(data)
        assert result.shape == (n_nodes, 3, n_frames)

    def test_3d_input_same_object(self):
        """3-D passthrough returns the exact same array (no copy)."""
        data = np.random.rand(4, 3, 10)
        result = view.prepare_animation_displacements(data)
        assert result is data

    def test_3d_input_n_nodes_mismatch_raises(self):
        """Supplying wrong n_nodes with 3-D input raises ValueError."""
        data = np.random.rand(6, 3, 10)
        with pytest.raises(ValueError):
            view.prepare_animation_displacements(data, n_nodes=5)

    def test_3d_input_n_frames_mismatch_raises(self):
        """Supplying wrong n_frames with 3-D input raises ValueError."""
        data = np.random.rand(6, 3, 10)
        with pytest.raises(ValueError):
            view.prepare_animation_displacements(data, n_frames=99)

    # -- 2-D input: (n_nodes, 3) → sine wave → (n_nodes, 3, n_frames) -------

    def test_2d_nodal_3dof_default_frames(self):
        """2-D (n_nodes, 3) with default n_frames produces (n_nodes, 3, 100)."""
        n_nodes = 6
        data = np.random.rand(n_nodes, 3)
        result = view.prepare_animation_displacements(data)
        assert result.shape == (n_nodes, 3, 100)

    def test_2d_nodal_3dof_custom_frames(self):
        """2-D (n_nodes, 3) with explicit n_frames produces correct shape."""
        n_nodes, n_frames = 4, 50
        data = np.random.rand(n_nodes, 3)
        result = view.prepare_animation_displacements(data, n_frames=n_frames)
        assert result.shape == (n_nodes, 3, n_frames)

    def test_2d_nodal_6dof_shape(self):
        """2-D (n_nodes, 6) → sine wave over all 6 DOFs → (n_nodes, 6, 100).

        When data.shape[1] is in range(3, 7) the code takes the 'pass' branch
        and applies the cosine envelope across ALL DOF columns; it does NOT
        truncate to 3.  Truncation to 3 only happens in the flat
        (n_nodes*n_dof, n_frames) layout.
        """
        n_nodes = 5
        data = np.random.rand(n_nodes, 6)
        result = view.prepare_animation_displacements(data)
        assert result.shape == (n_nodes, 6, 100)

    def test_2d_flat_6dof_shape(self):
        """2-D (n_nodes*6, n_frames) flattened layout → (n_nodes, 3, n_frames)."""
        n_nodes, n_frames = 3, 20
        data = np.random.rand(n_nodes * 6, n_frames)
        result = view.prepare_animation_displacements(data, n_nodes=n_nodes)
        assert result.shape == (n_nodes, 3, n_frames)

    # -- 1-D input: (n_nodes*3,) → sine wave → (n_nodes, 3, 100) ------------

    def test_1d_flat_3dof_default_frames(self):
        """1-D (n_nodes*3,) with default n_frames → (n_nodes, 3, 100)."""
        n_nodes = 6
        data = np.random.rand(n_nodes * 3)
        result = view.prepare_animation_displacements(data, n_nodes=n_nodes)
        assert result.shape == (n_nodes, 3, 100)

    def test_1d_flat_6dof_shape(self):
        """1-D (n_nodes*6,) → only first 3 DOFs kept → (n_nodes, 3, 100)."""
        n_nodes = 4
        data = np.random.rand(n_nodes * 6)
        result = view.prepare_animation_displacements(data, n_nodes=n_nodes)
        assert result.shape == (n_nodes, 3, 100)

    def test_1d_missing_n_nodes_raises(self):
        """1-D input without n_nodes raises ValueError."""
        data = np.random.rand(18)
        with pytest.raises(ValueError):
            view.prepare_animation_displacements(data)

    # -- Values: sine wave amplitude check -----------------------------------

    def test_2d_real_input_amplitude(self):
        """For real 2-D input the cosine envelope preserves amplitude: max == data max."""
        n_nodes = 3
        data = np.ones((n_nodes, 3))  # all ones → amplitude is 1
        result = view.prepare_animation_displacements(data)
        # cos oscillates between -1 and 1; abs(data) == 1 so max over frames == 1
        assert np.isclose(result.max(), 1.0, atol=1e-9)


# ---------------------------------------------------------------------------
# 3.  prepare_animation_field
# ---------------------------------------------------------------------------

class TestPrepareAnimationField:
    """Tests for view.prepare_animation_field(data, n_nodes, n_frames)."""

    # -- 2-D input: (n_nodes, n_frames) returned as-is ----------------------

    def test_2d_passthrough_shape(self):
        """2-D (n_nodes, n_frames) is returned as-is."""
        n_nodes, n_frames = 6, 20
        data = np.random.rand(n_nodes, n_frames)
        result = view.prepare_animation_field(data)
        assert result.shape == (n_nodes, n_frames)

    def test_2d_passthrough_same_object(self):
        """2-D passthrough returns the exact same array."""
        data = np.random.rand(6, 20)
        result = view.prepare_animation_field(data)
        assert result is data

    def test_2d_n_nodes_mismatch_raises(self):
        """Wrong n_nodes with 2-D input raises ValueError."""
        data = np.random.rand(6, 20)
        with pytest.raises(ValueError):
            view.prepare_animation_field(data, n_nodes=5)

    def test_2d_n_frames_mismatch_raises(self):
        """Wrong n_frames with 2-D input raises ValueError."""
        data = np.random.rand(6, 20)
        with pytest.raises(ValueError):
            view.prepare_animation_field(data, n_frames=99)

    # -- 1-D input: (n_nodes,) → sine wave → (n_nodes, n_frames) ------------

    def test_1d_default_frames(self):
        """1-D (n_nodes,) with default n_frames → (n_nodes, 100)."""
        n_nodes = 6
        data = np.random.rand(n_nodes)
        result = view.prepare_animation_field(data, n_nodes=n_nodes)
        assert result.shape == (n_nodes, 100)

    def test_1d_custom_frames(self):
        """1-D (n_nodes,) with custom n_frames → (n_nodes, n_frames)."""
        n_nodes, n_frames = 4, 50
        data = np.random.rand(n_nodes)
        result = view.prepare_animation_field(data, n_nodes=n_nodes, n_frames=n_frames)
        assert result.shape == (n_nodes, n_frames)

    def test_1d_missing_n_nodes_raises(self):
        """1-D input without n_nodes raises ValueError."""
        data = np.random.rand(6)
        with pytest.raises(ValueError):
            view.prepare_animation_field(data)

    # -- Values: cosine envelope amplitude check -----------------------------

    def test_1d_real_input_amplitude(self):
        """For real 1-D ones input the cosine envelope max equals 1."""
        n_nodes = 4
        data = np.ones(n_nodes)
        result = view.prepare_animation_field(data, n_nodes=n_nodes)
        assert np.isclose(result.max(), 1.0, atol=1e-9)

    def test_1d_zero_input_stays_zero(self):
        """Zero field stays zero across all frames."""
        n_nodes = 4
        data = np.zeros(n_nodes)
        result = view.prepare_animation_field(data, n_nodes=n_nodes)
        assert np.all(result == 0.0)


# ---------------------------------------------------------------------------
# 4.  Plotter3D ImportError guard (PyQt6 absent)
# ---------------------------------------------------------------------------

class TestPlotter3DImportGuard:
    """Verify the PyQt6 guard in Plotter3D.__init__."""

    def test_raises_when_pyqt6_absent(self):
        """Without PyQt6 instantiating Plotter3D must raise ImportError."""
        if importlib.util.find_spec("PyQt6") is not None:
            pytest.skip("PyQt6 is installed — cannot test the absent-PyQt6 guard")

        with pytest.raises(ImportError) as exc_info:
            view.Plotter3D()

        assert "PyQt6" in str(exc_info.value), (
            f"ImportError message should mention 'PyQt6', got: {exc_info.value}"
        )
