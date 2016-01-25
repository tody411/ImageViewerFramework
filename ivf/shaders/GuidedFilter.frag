uniform sampler2D guideTex;
uniform sampler2D colorTex;

uniform float sigmaSpace;
uniform float sigmaRange;
uniform int numSamples;

void main (void)
{

    vec4 c_sum = vec4(0, 0, 0, 0);
    float w_sum = 0.0;

    vec2 uv = gl_TexCoord[0].st;
	vec4 g_p = texture2D(guideTex, uv);
    vec4 c_p = texture2D(colorTex, uv);

    float sigmaRange2 = sigmaRange * sigmaRange;

    float sSigmaSpace = sigmaSpace / 1024.0;
    float sigmaSpace2 = sSigmaSpace * sSigmaSpace;

    float ksize = 2.0 * sSigmaSpace;
    float stepsize = 2.0 * ksize / float(numSamples);

    for (int yi = 0; yi < numSamples; ++yi)
    {
        float dy = yi * stepsize - ksize;

        for(int xi = 0; xi < numSamples; ++xi)
        {
            float dx = xi * stepsize - ksize;
            vec2 offset = vec2( dx, dy);
            vec2 q = uv + offset;
            vec4 g_q = texture2D(guideTex, q );
            vec4 c_q = texture2D(colorTex,  q );

            float d_g = length(g_q - g_p);
            float d_s = length(offset);

            float w_g =  exp( - d_g *d_g / sigmaRange2 );
            float w_s = exp( - d_s *d_s / sigmaSpace2 );
            float w = w_g * w_s;

            c_sum += w * c_q;
            w_sum += w;
        }

    }

    vec4 c = c_sum / w_sum;
    c.a = c_p.a;
    gl_FragColor = c;
}