from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# SAFEST: allow CORS fully for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TEMP: allow any frontend (lock this down later)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Preflight OPTIONS fallback for safety (force-handle any failing preflight requests)
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return {"status": "Preflight OK"}

# Simple healthcheck
@app.get("/")
async def root():
    return {"message": "NLP to Shader API is running!"}

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")


FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "Generate a GLSL fragment shader that creates a cube with the faces of a die."
    },
    {
        "role": "assistant",
        "content": """#ifdef GL_ES
precision mediump float;
#endif

uniform float u_time;
uniform vec2 u_resolution;
varying vec2 vUv;
varying vec3 vNormal;
varying float vFaceIndex;

void main() {
    vec2 uv = vUv;
    int faceIndex = int(vFaceIndex);
    
    vec3 color;
    
    // Face 0: One dot (Right face)
    if (faceIndex == 0) {
        if (distance(uv, vec2(0.5, 0.5)) < 0.1) {
            color = vec3(0.0);
        } else {
            color = vec3(1.0, 0.7, 0.7); 
        }
    }
    // Face 1: Two dots (Left face)
    else if (faceIndex == 1) {
        if (distance(uv, vec2(0.3, 0.3)) < 0.1 || 
            distance(uv, vec2(0.7, 0.7)) < 0.1) {
            color = vec3(0.0);
        } else {
            color = vec3(0.7, 0.7, 1.0); 
        }
    }
    // Face 2: Three dots (Top face)
    else if (faceIndex == 2) {
        if (distance(uv, vec2(0.3, 0.3)) < 0.1 ||
            distance(uv, vec2(0.5, 0.5)) < 0.1 || 
            distance(uv, vec2(0.7, 0.7)) < 0.1) {
            color = vec3(0.0);
        } else {
            color = vec3(0.7, 1.0, 0.7); 
        }
    }
    // Face 3: Four dots (Bottom face)
    else if (faceIndex == 3) {
        if (distance(uv, vec2(0.3, 0.3)) < 0.1 ||
            distance(uv, vec2(0.3, 0.7)) < 0.1 ||
            distance(uv, vec2(0.7, 0.3)) < 0.1 ||
            distance(uv, vec2(0.7, 0.7)) < 0.1) {
            color = vec3(0.0);
        } else {
            color = vec3(1.0, 1.0, 0.7);
        }
    }
    // Face 4: Five dots (Front face)
    else if (faceIndex == 4) {
        if (distance(uv, vec2(0.3, 0.3)) < 0.1 ||
            distance(uv, vec2(0.3, 0.7)) < 0.1 ||
            distance(uv, vec2(0.5, 0.5)) < 0.1 ||
            distance(uv, vec2(0.7, 0.3)) < 0.1 ||
            distance(uv, vec2(0.7, 0.7)) < 0.1) {
            color = vec3(0.0);
        } else {
            color = vec3(1.0, 0.7, 1.0); 
        }
    }
    // Face 5: Six dots (Back face)
    else {
        if (distance(uv, vec2(0.3, 0.3)) < 0.1 ||
            distance(uv, vec2(0.3, 0.5)) < 0.1 ||
            distance(uv, vec2(0.3, 0.7)) < 0.1 ||
            distance(uv, vec2(0.7, 0.3)) < 0.1 ||
            distance(uv, vec2(0.7, 0.5)) < 0.1 ||
            distance(uv, vec2(0.7, 0.7)) < 0.1) {
            color = vec3(0.0);
        } else {
            color = vec3(0.7, 1.0, 1.0); 
        }
    }
    
    gl_FragColor = vec4(color, 1.0);
}"""
    },
    {
        "role": "user",
        "content": "Minecraft Dirt Block."
    },
    {
        "role": "assistant",
        "content": """#ifdef GL_ES
precision mediump float;
#endif

varying vec2 vUv;
varying float vFaceIndex;

float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
}

void main() {
    vec2 uv = vUv;
    float pixelSize = 1.0 / 16.0;
    uv = floor(uv / pixelSize) * pixelSize;

    int faceIndex = int(vFaceIndex);
    vec3 color;

    if (faceIndex == 2) {
        float noise = random(uv * 16.0);
        color = mix(vec3(0.2, 0.6, 0.2), vec3(0.1, 0.4, 0.1), noise);
    } else {
        float noise = random(uv * 16.0);
        color = mix(vec3(0.4, 0.3, 0.1), vec3(0.3, 0.2, 0.05), noise);
    }

    gl_FragColor = vec4(color, 1.0);
}
"""
    },
        {
        "role": "user",
        "content": "Earth-like sphere."
    },
    {
        "role": "assistant",
        "content": """#ifdef GL_ES
precision mediump float;
#endif

varying vec2 vUv;

float random(vec2 st) {
    return fract(sin(dot(st, vec2(12.9898,78.233))) * 43758.5453);
}

float noise(vec2 st) {
    vec2 i = floor(st);
    vec2 f = fract(st);
    
    float a = random(i);
    float b = random(i + vec2(1.0, 0.0));
    float c = random(i + vec2(0.0, 1.0));
    float d = random(i + vec2(1.0, 1.0));
    
    vec2 u = f * f * (3.0 - 2.0 * f);
    
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

float fbm(vec2 st) {
    float value = 0.0;
    float amplitude = 0.5;
    for (int i = 0; i < 5; i++) {
        value += amplitude * noise(st);
        st *= 2.0;
        amplitude *= 0.5;
    }
    return value;
}

void main() {
    vec2 uv = vUv;
    uv.y = 1.0 - uv.y;

    float sphereBlend = smoothstep(0.0, 1.0, 1.0 - abs(uv.y - 0.5) * 2.0);
    vec2 spherical = vec2(uv.x, uv.y * sphereBlend);

    float landNoise = fbm(spherical * 8.0 + vec2(1.0, 0.0));
    float landMask = smoothstep(0.48, 0.5, landNoise);

    float cloudNoise = fbm(spherical * 16.0 + vec2(4.2, 3.3));
    float cloudMask = smoothstep(0.6, 0.75, cloudNoise);

    vec3 oceanColor = vec3(0.0, 0.2, 0.5);
    vec3 landColor = vec3(0.1, 0.6, 0.2);
    vec3 cloudColor = vec3(1.0);

    vec3 surfaceColor = mix(oceanColor, landColor, landMask);
    vec3 finalColor = mix(surfaceColor, cloudColor, cloudMask * 0.5);

    gl_FragColor = vec4(finalColor, 1.0);
}
"""
    }
]

@app.get("/")
async def root():
    return {"message": "NLP to Shader API is running!"}

@app.post("/generate")
async def generate(request: Request):
    body = await request.json()
    prompt = body.get("prompt")

    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
    }

    payload = {
    "model": "claude-3-7-sonnet-20250219",
    "max_tokens": 2048,
    "temperature": 0.3,
    # SYSTEM PROMPT
    "messages": [
        {
            "role": "user",
            "content": """
            You are an expert in GLSL fragment shader programming.

            Your task:
            - Generate a valid GLSL fragment shader
            - The shader must include a void main() function
            - You must define gl_FragColor inside main()
            - At the top, always include:
                #ifdef GL_ES
                precision mediump float;
                #endif
            - Always include these uniforms at the top:
                uniform float u_time;
                uniform vec2 u_resolution;
            - You may use either u_time/u_resolution or time/resolution in your code (both are available and equivalent)
            - For normalized coordinates, use either gl_FragCoord.xy / u_resolution.xy or gl_FragCoord.xy / resolution.xy
            - Use animated effects if relevant (e.g., sine waves using time)
            - Do NOT assume any texture samplers like iChannel0 or iResolution
            - Do NOT use external inputs like textures or buffers
            - Only use UV coordinates (from gl_FragCoord) and time to create procedural visual effects
            - Output pure procedural shaders (no textures)
            - Do not include comments, explanations, markdown, or extra text
            - Output ONLY raw shader code below. 
            """
        },
        *FEW_SHOT_EXAMPLES,
        {
            "role": "user",
            "content": f"Description: {prompt}"
        }
    ],
    }


    response = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
    return response.json()
