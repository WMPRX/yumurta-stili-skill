// post.js — the look, in one WebGL pass (analiz/renk.md, analiz/doku.md):
//   1. sepia grade: partial desaturation, warm gain/lift (measured white point ≈ rgb 215-237 / 193-217 / 180-204, black ≈ 6-17 / 1-5 / 0-2)
//   2. heavy vignette (measured corner/centre ≈ 0.25)
//   3. CRT scanlines: period 1.445 % of the height (27.75 px at 1920), ±3.6 % brightness, sliding DOWN 0.45 px/frame at 1920
//   4. faint grain, end-card darkening
// Tune per story with the `look` object returned by frame(): { sat, gain, lift, gamma, vig, scan, grain, dim, exposure }.
export const LOOK = {
  sat: .42,                     // 0 = monochrome sepia, 1 = original colours
  gain: [.94, .845, .765],      // white maps here
  lift: [.022, .006, .0],       // black maps here
  gamma: 1.08,
  exposure: 1.0,
  vig: .62,                     // vignette strength
  vigIn: .28,                   // where it starts (0 centre … 1 corner)
  scan: .036,                   // scanline amplitude
  scanPeriod: .014453,          // fraction of the height
  scanSpeed: .000234,           // fraction of the height per frame (downwards)
  grain: .012,
  dim: 0,                       // end card: 0..1 darkens everything drawn so far
};

const VS = `attribute vec2 p; varying vec2 uv; void main(){ uv = p * .5 + .5; gl_Position = vec4(p, 0., 1.); }`;
const FS = `precision highp float;
varying vec2 uv; uniform sampler2D tex; uniform vec2 res; uniform float frame;
uniform float sat, gamma, exposure, vig, vigIn, scan, scanPeriod, scanSpeed, grain, dim; uniform vec3 gain, lift;
float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
void main(){
  vec2 st = vec2(uv.x, 1. - uv.y);
  vec3 c = texture2D(tex, vec2(uv.x, uv.y)).rgb * exposure;
  float l = dot(c, vec3(.2126, .7152, .0722));
  c = mix(vec3(l), c, sat);
  c = pow(clamp(c, 0., 1.), vec3(gamma));
  c = lift + c * (gain - lift);
  c *= 1. - dim;
  vec2 d = (st - .5) * 2.; float r = length(d) / 1.41421;
  c *= 1. - vig * smoothstep(vigIn, 1.05, r);
  float y = st.y * res.y;
  float per = scanPeriod * res.y;
  c *= 1. + scan * sin(6.2831853 * (y - frame * scanSpeed * res.y) / per);
  c += (h(st * res + frame * 1.7) - .5) * grain;
  gl_FragColor = vec4(clamp(c, 0., 1.), 1.);
}`;

export class Post {
  constructor(canvas, W, H) {
    this.W = W; this.H = H; canvas.width = W; canvas.height = H;
    const gl = this.gl = canvas.getContext('webgl', { preserveDrawingBuffer: true, premultipliedAlpha: false });
    if (!gl) throw new Error('WebGL yok / no WebGL');
    const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
    const pr = this.pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(pr); gl.useProgram(pr);
    const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    this.tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, this.tex);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    this.u = n => gl.getUniformLocation(pr, n);
  }
  render(src, frame, look = {}) {
    const gl = this.gl, L = { ...LOOK, ...look };
    gl.viewport(0, 0, this.W, this.H);
    gl.bindTexture(gl.TEXTURE_2D, this.tex); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src);
    gl.uniform2f(this.u('res'), this.W, this.H); gl.uniform1f(this.u('frame'), frame);
    for (const k of ['sat', 'gamma', 'exposure', 'vig', 'vigIn', 'scan', 'scanPeriod', 'scanSpeed', 'grain', 'dim']) gl.uniform1f(this.u(k), L[k]);
    gl.uniform3fv(this.u('gain'), L.gain); gl.uniform3fv(this.u('lift'), L.lift);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }
}
