uniform sampler2D guideTex;
uniform sampler2D colorTex;

vec4 diffusion(in vec2 uv, in vec2 offset, inout float w_sum)
{
    vec2 q = uv + offset;
    vec4 g_q = texture2D(guideTex, q);
    vec4 c_q = texture2D(colorTex, q);
    float w_q = 10.0 * g_q.a + c_q.a + 0.001;
    w_sum += w_q;
    return w_q * c_q;
}

void main (void)
{
    vec2 uv = gl_TexCoord[0].st;
	vec4 g_p = texture2D(guideTex, uv);
    vec4 c_p = texture2D(colorTex, uv);

    float delta = 1.0 / 1024.0;
    vec4 c_sum = vec4(0, 0, 0, 0);
    float w_sum = 0.0;
    c_sum = diffusion(uv, vec2(-delta, 0), w_sum)
          + diffusion(uv, vec2( delta, 0), w_sum)
          + diffusion(uv, vec2( 0, delta), w_sum)
          + diffusion(uv, vec2( 0, -delta), w_sum);
    vec4 c = c_sum / w_sum;

    if (g_p.a > 0.99)
    {
        c = g_p;
    }
    c.a = 1.0;
    gl_FragColor = c;
}