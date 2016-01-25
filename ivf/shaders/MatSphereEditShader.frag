uniform sampler2D tex;

void main (void)
{
   vec3 L = gl_LightSource[0].position.xyz;
   float Ka = gl_LightSource[0].ambient.x;
   float Kd = gl_LightSource[0].diffuse.x;

   vec2 xy = 2.0 * gl_TexCoord[0].st - vec2(1.0, 1.0);
   float r = length(xy);

   float z = sqrt( max( 0.0, 1.0 - r) );
   vec3 N = normalize( vec3( xy, z) );
   float I = Ka + Kd * dot(N, L);

   vec4 color = texture2D(tex, vec2(I, 0.0));

   vec3 N_color = 0.5 * N + vec3(0.5, 0.5, 0.5);
   float alpha = smoothstep(1.0, 0.99, r);
   color.a = min(alpha, color.a);
   gl_FragColor = color;
}