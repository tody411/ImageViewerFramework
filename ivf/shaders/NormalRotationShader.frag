uniform sampler2D tex;
uniform float rotation;

void main (void)
{
	vec4 N_color = texture2D(tex, gl_TexCoord[0].st);
	float alpha = N_color.a;
	vec3 N = normalize( 2.0 * N_color.xyz - vec3(1.0, 1.0, 1.0) );
	vec2 u_new = vec2( cos(-rotation), sin(-rotation) );
	vec2 v_new = vec2( -sin(-rotation), cos(-rotation) );
	vec2 N_xy_new = N.x * u_new + N.y * v_new;
	N.xy = N_xy_new;
	N = normalize(N);

	N_color.xyz = 0.5 * N + vec3(0.5, 0.5, 0.5);
	N_color.xyz = clamp(N_color.xyz, 0.0, 1.0);
    gl_FragColor = N_color;
}