uniform sampler2D normalTex;
uniform sampler2D colorTex;

void main (void)
{
	vec4 N_color = texture2D(normalTex, gl_TexCoord[0].st);
	vec3 N = normalize( 2.0 * N_color.xyz - vec3(1.0, 1.0, 1.0) );
	vec3 L0 = gl_LightSource[1].position.xyz;

	vec4 c = texture2D(colorTex, gl_TexCoord[0].st);

	vec3 L = gl_LightSource[0].position.xyz;
	vec4 Ka = gl_LightSource[0].ambient;
	vec4 Kd = gl_LightSource[0].diffuse;

	float dI = clamp(dot(L, N), 0.0, 1.0) - clamp(dot(L0, N), 0.0, 1.0);
	vec4 dc = Kd * dI;

	float alpha = c.a;

	vec4 c_new = c;
	c_new.rgb = c.rgb + dc.rgb;
	gl_FragColor = c_new;
}