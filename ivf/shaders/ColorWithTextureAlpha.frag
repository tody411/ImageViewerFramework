uniform vec4 color;
uniform sampler2D tex;

void main (void)
{
	vec4 texColor = texture2D(tex, gl_TexCoord[0].st);
	gl_FragColor = color;
	gl_FragColor.a = texColor.a;
}