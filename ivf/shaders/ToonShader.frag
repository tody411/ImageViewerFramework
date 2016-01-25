uniform sampler2D normalTex;
uniform sampler2D colorMapTex;

void main (void)
{
	vec4 N_color = texture2D(normalTex, gl_TexCoord[0].st);
	vec3 N = normalize( 2.0 * N_color.xyz - vec3(1.0, 1.0, 1.0) );

	vec3 L = gl_LightSource[0].position.xyz;
	float Ka = gl_LightSource[0].ambient.x;
	float Kd = gl_LightSource[0].diffuse.x;

	//float I = Ka + Kd * dot( L, N );
	float I = dot( L, N );
	I = clamp( I, 0.05, 0.95);

	vec4 c = texture2D(colorMapTex, vec2(I, 0.5));
	float alpha = N_color.a;

	c.a = alpha;
	gl_FragColor = c;
}