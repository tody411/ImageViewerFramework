uniform sampler2D colorTex;
uniform sampler2D normalTex;

void main (void)
{
	vec4 N_color = texture2D(normalTex, gl_TexCoord[0].st);
	vec3 N = normalize( 2.0 * N_color.xyz - vec3(1.0, 1.0, 1.0) );
	vec3 L0 = vec3(0,0,1);
	float LdN0 = 0.5 * dot(L0, N) + 0.5;

	vec4 c = texture2D(colorTex, gl_TexCoord[0].st);
	float I0 = (c.x + c.y + c.z ) / 3.0;
	float Kd0 = I0 / LdN0;

	vec3 L = gl_LightSource[0].position.xyz;
	float Ka = gl_LightSource[0].ambient.x;
	float Kd = gl_LightSource[0].diffuse.x;

	float dI = Ka + Kd * Kd0 * dot( L - L0, N );
	float I = max( 0.0, I0 + dI);
	float alpha = c.a;

	//N_color.a = c.a;

	vec4 c_new = c;
	c_new.rgb = clamp( I * c.rgb / I0, 0.0, 1.0);
	//N_color.xyz = 0.5 * N + 0.5 * c.rgb;
	//c.a = dot(L, N);
    gl_FragColor = c_new;
    //gl_FragColor = N_color;
}