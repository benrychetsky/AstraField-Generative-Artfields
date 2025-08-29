import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Box, Container, Grid, Card, CardContent, CardHeader,
  Typography, Button, Slider, Switch, FormControlLabel, TextField,
  Select, MenuItem, InputLabel, FormControl, LinearProgress, Stack,
  Divider, Chip
} from "@mui/material";
import RefreshIcon from "@mui/icons-material/Refresh";
import DownloadIcon from "@mui/icons-material/Download";
import ImageIcon from "@mui/icons-material/Image";
import { getJSON, postForm } from "../utils/http";

type PresetsResponse = Record<string, any>;

const sliderSx = { mt: 1, mb: 2 };

export default function CoverPlayground() {
  const fileRef = useRef<HTMLInputElement>(null);
  const [imgUrl, setImgUrl] = useState<string>();
  const [loading, setLoading] = useState(false);
  const [presets, setPresets] = useState<string[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<string>("default");

  // core params matching your backend GenerateParams
  const [params, setParams] = useState({
    // output & grade
    size: 1024,
    tone_lo: "#050a10",
    tone_hi: "#12cabf",
    tone_strength: 0.9,
    seed: "" as string | number | "",

    // grid
    grid_n: 16,

    // toggles
    use_dots: false,
    use_lines: true,
    use_contours: true,
    use_arcs: true,
    use_blocks: true,

    // dots
    dot_step: 40,
    dot_min: 1.0,
    dot_max: 9.0,

    // lines
    line_angle_deg: 22,
    line_density: 110,
    line_lw: 1.0,
    line_alpha: 0.22,

    // contours
    contour_levels: 8,
    contour_alpha: 0.30,
    contour_lw: 1.1,

    // arcs
    arc_count: 6,
    arc_rmin: 0.07,
    arc_rmax: 0.24,
    arc_jitter: 0.012,
    arc_lw: 2.0,
    arc_alpha: 0.9,

    // blocks
    block_count: 2,
  });

  // Load preset names
  useEffect(() => {
    (async () => {
      try {
        const r = await getJSON<PresetsResponse>("/presets");
        setPresets(Object.keys(r));
      } catch {
        // ignore silently
      }
    })();
  }, []);

  async function applyPreset(name: string) {
    try {
      const r = await getJSON<PresetsResponse>("/presets");
      if (r[name]) {
        setParams(p => ({ ...p, ...r[name] }));
      }
      setSelectedPreset(name);
    } catch (e) {
      console.error(e);
    }
  }

  function set<K extends keyof typeof params>(key: K, value: (typeof params)[K]) {
    setParams(prev => ({ ...prev, [key]: value }));
  }

  async function generate() {
    setLoading(true);
    try {
      const fd = new FormData();
      const f = fileRef.current?.files?.[0];
      if (f) fd.append("photo", f);

      // append all params as strings (FastAPI Form reads strings)
      Object.entries(params).forEach(([k, v]) => fd.append(k, String(v ?? "")));

      const blob = (await postForm("/generate", fd)) as Blob;
      setImgUrl(URL.createObjectURL(blob));
    } catch (e: any) {
      alert(`Generate failed: ${e.message ?? e}`);
    } finally {
      setLoading(false);
    }
  }

  function download() {
    if (!imgUrl) return;
    const a = document.createElement("a");
    a.href = imgUrl;
    a.download = "astrafield-cover.png";
    a.click();
  }

  const leftCard = useMemo(() => (
    <Card elevation={3} sx={{ borderRadius: 3 }}>
      <CardHeader title="AstraField Controls" subheader="Play with geometry + palette" />
      <CardContent>
        <Stack spacing={2}>
          {/* Presets */}
          <FormControl fullWidth>
            <InputLabel id="preset-label">Preset</InputLabel>
            <Select
              labelId="preset-label"
              label="Preset"
              value={selectedPreset}
              onChange={(e) => applyPreset(e.target.value as string)}
            >
              {presets.length === 0 && <MenuItem value="default">default</MenuItem>}
              {presets.map(k => <MenuItem key={k} value={k}>{k}</MenuItem>)}
            </Select>
          </FormControl>

          <Divider><Chip label="Image & Palette" size="small" /></Divider>
          <Button
            variant="outlined"
            startIcon={<ImageIcon />}
            onClick={() => fileRef.current?.click()}
          >
            Choose Photo
          </Button>
          <input ref={fileRef} type="file" accept="image/*" hidden />

          <Grid container spacing={2}>
            <Grid size={6}>
              <TextField
                label="Low Tone"
                type="color"
                fullWidth
                value={params.tone_lo}
                onChange={e => set("tone_lo", e.target.value)}
              />
            </Grid>
            <Grid size={6}>
              <TextField
                label="High Tone"
                type="color"
                fullWidth
                value={params.tone_hi}
                onChange={e => set("tone_hi", e.target.value)}
              />
            </Grid>
            <Grid size={12}>
              <Typography variant="body2">Tone Strength: {params.tone_strength}</Typography>
              <Slider sx={sliderSx} min={0} max={1} step={0.01}
                value={params.tone_strength}
                onChange={(_, v) => set("tone_strength", v as number)} />
            </Grid>
            <Grid size={12}>
              <Typography variant="body2">Output Size: {params.size}px</Typography>
              <Slider sx={sliderSx} min={512} max={2048} step={128}
                value={params.size}
                onChange={(_, v) => set("size", v as number)} />
            </Grid>
            <Grid size={12}>
              <TextField
                label="Seed (optional)"
                placeholder="e.g. 42"
                value={params.seed}
                onChange={e => set("seed", e.target.value)}
                fullWidth
              />
            </Grid>
          </Grid>

          <Divider><Chip label="Layers" size="small" /></Divider>
          <Grid container>
            <Grid size={6}><FormControlLabel control={<Switch checked={params.use_lines} onChange={(_, c) => set("use_lines", c)} />} label="Lines" /></Grid>
            <Grid size={6}><FormControlLabel control={<Switch checked={params.use_contours} onChange={(_, c) => set("use_contours", c)} />} label="Contours" /></Grid>
            <Grid size={6}><FormControlLabel control={<Switch checked={params.use_arcs} onChange={(_, c) => set("use_arcs", c)} />} label="Arcs" /></Grid>
            <Grid size={6}><FormControlLabel control={<Switch checked={params.use_blocks} onChange={(_, c) => set("use_blocks", c)} />} label="Blocks" /></Grid>
            <Grid size={6}><FormControlLabel control={<Switch checked={params.use_dots} onChange={(_, c) => set("use_dots", c)} />} label="Dots" /></Grid>
          </Grid>

          {/* Lines */}
          <Divider><Chip label="Lines" size="small" /></Divider>
          <Typography variant="body2">Angle: {params.line_angle_deg}°</Typography>
          <Slider sx={sliderSx} min={-90} max={90} step={1}
            value={params.line_angle_deg}
            onChange={(_, v) => set("line_angle_deg", v as number)} />
          <Typography variant="body2">Density: {params.line_density}</Typography>
          <Slider sx={sliderSx} min={10} max={300} step={1}
            value={params.line_density}
            onChange={(_, v) => set("line_density", v as number)} />
          <Typography variant="body2">Thickness: {params.line_lw}</Typography>
          <Slider sx={sliderSx} min={0.5} max={5} step={0.1}
            value={params.line_lw}
            onChange={(_, v) => set("line_lw", v as number)} />
          <Typography variant="body2">Opacity: {params.line_alpha.toFixed(2)}</Typography>
          <Slider sx={sliderSx} min={0} max={1} step={0.01}
            value={params.line_alpha}
            onChange={(_, v) => set("line_alpha", v as number)} />

          {/* Contours */}
          <Divider><Chip label="Contours" size="small" /></Divider>
          <Typography variant="body2">Levels: {params.contour_levels}</Typography>
          <Slider sx={sliderSx} min={2} max={30} step={1}
            value={params.contour_levels}
            onChange={(_, v) => set("contour_levels", v as number)} />
          <Typography variant="body2">Thickness: {params.contour_lw}</Typography>
          <Slider sx={sliderSx} min={0.5} max={6} step={0.1}
            value={params.contour_lw}
            onChange={(_, v) => set("contour_lw", v as number)} />
          <Typography variant="body2">Opacity: {params.contour_alpha.toFixed(2)}</Typography>
          <Slider sx={sliderSx} min={0} max={1} step={0.01}
            value={params.contour_alpha}
            onChange={(_, v) => set("contour_alpha", v as number)} />

          {/* Arcs */}
          <Divider><Chip label="Arcs" size="small" /></Divider>
          <Typography variant="body2">Count: {params.arc_count}</Typography>
          <Slider sx={sliderSx} min={1} max={20} step={1}
            value={params.arc_count}
            onChange={(_, v) => set("arc_count", v as number)} />
          <Typography variant="body2">Inner/Outer Radius</Typography>
          <Stack direction="row" spacing={2}>
            <Slider sx={{ ...sliderSx, flex: 1 }} min={0.02} max={0.5} step={0.002}
              value={params.arc_rmin}
              onChange={(_, v) => set("arc_rmin", v as number)} />
            <Slider sx={{ ...sliderSx, flex: 1 }} min={0.02} max={0.8} step={0.002}
              value={params.arc_rmax}
              onChange={(_, v) => set("arc_rmax", v as number)} />
          </Stack>
          <Typography variant="body2">Jitter: {params.arc_jitter.toFixed(3)}</Typography>
          <Slider sx={sliderSx} min={0} max={0.05} step={0.001}
            value={params.arc_jitter}
            onChange={(_, v) => set("arc_jitter", v as number)} />
          <Typography variant="body2">Thickness: {params.arc_lw}</Typography>
          <Slider sx={sliderSx} min={0.5} max={8} step={0.1}
            value={params.arc_lw}
            onChange={(_, v) => set("arc_lw", v as number)} />
          <Typography variant="body2">Opacity: {params.arc_alpha.toFixed(2)}</Typography>
          <Slider sx={sliderSx} min={0} max={1} step={0.01}
            value={params.arc_alpha}
            onChange={(_, v) => set("arc_alpha", v as number)} />

          {/* Blocks & Dots quick controls */}
          <Divider><Chip label="Blocks & Dots" size="small" /></Divider>
          <Typography variant="body2">Block Count: {params.block_count}</Typography>
          <Slider sx={sliderSx} min={0} max={8} step={1}
            value={params.block_count}
            onChange={(_, v) => set("block_count", v as number)} />

          {params.use_dots && (
            <>
              <Typography variant="body2">Dot Step: {params.dot_step}</Typography>
              <Slider sx={sliderSx} min={10} max={120} step={1}
                value={params.dot_step}
                onChange={(_, v) => set("dot_step", v as number)} />
              <Typography variant="body2">Dot Size: {params.dot_min} - {params.dot_max}</Typography>
              <Stack direction="row" spacing={2}>
                <Slider sx={{ ...sliderSx, flex: 1 }} min={0.2} max={20} step={0.2}
                  value={params.dot_min}
                  onChange={(_, v) => set("dot_min", v as number)} />
                <Slider sx={{ ...sliderSx, flex: 1 }} min={0.2} max={20} step={0.2}
                  value={params.dot_max}
                  onChange={(_, v) => set("dot_max", v as number)} />
              </Stack>
            </>
          )}

          <Stack direction="row" spacing={1}>
            <Button
              variant="contained"
              startIcon={<RefreshIcon />}
              onClick={generate}
              disabled={loading}
            >
              {loading ? "Generating..." : "Generate"}
            </Button>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={download}
              disabled={!imgUrl}
            >
              Download
            </Button>
          </Stack>
          {loading && <LinearProgress sx={{ mt: 1 }} />}
        </Stack>
      </CardContent>
    </Card>
  ), [params, presets, selectedPreset, loading, imgUrl]);

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 4, lg: 3 }}>{leftCard}</Grid>
        <Grid size={{ xs: 12, md: 8, lg: 9 }}>
          <Card elevation={3} sx={{ borderRadius: 3, height: "calc(100vh - 120px)" }}>
            <CardHeader title="Preview" subheader="Your generated artwork" />
            <CardContent sx={{ height: "100%", display: "grid", placeItems: "center", bgcolor: "#0e0e11" }}>
              {imgUrl ? (
                <Box component="img"
                  src={imgUrl}
                  alt="AstraField preview"
                  sx={{ maxWidth: "100%", maxHeight: "75vh", borderRadius: 2, boxShadow: 3 }}
                />
              ) : (
                <Typography variant="body2" color="grey.400">Choose a photo and hit Generate</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}
