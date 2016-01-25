uniform sampler2D tex;

void main (void)
{
	vec4 c = texture2D(tex, gl_TexCoord[0].st);
	//c.xyz = c.a * c.xyz;
   	gl_FragColor = c;
   //gl_FragColor = texture2D(tex, vec2(0.3, 0.3));
}