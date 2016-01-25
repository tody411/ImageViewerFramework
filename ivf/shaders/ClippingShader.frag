uniform sampler2D colorTex;
uniform sampler2D alphaTex;

uniform float reverseAlpha;

void main (void)
{
	vec4 c = texture2D(colorTex, gl_TexCoord[0].st);
	vec4 a = texture2D(alphaTex, gl_TexCoord[0].st);
	c.a = mix( a.a, 1.0 - a.a, reverseAlpha);

    gl_FragColor = c;
}