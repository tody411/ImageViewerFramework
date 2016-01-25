uniform sampler2D normalTex;

void main (void)
{
	vec4 N_color = texture2D(normalTex, gl_TexCoord[0].st);
	vec3 N = normalize( 2.0 * N_color.xyz - vec3(1.0, 1.0, 1.0) );

	vec3 L = gl_LightSource[0].position.xyz;
	float Ka = gl_LightSource[0].ambient.x;
	float Kd = gl_LightSource[0].diffuse.x;

	float I = Ka + Kd * dot( L, N );
	I = clamp( I, 0.0, 1.0);
	float alpha = N_color.a;

	vec4 c_new = vec4(I, I, I, alpha);
	gl_FragColor = c_new;
}