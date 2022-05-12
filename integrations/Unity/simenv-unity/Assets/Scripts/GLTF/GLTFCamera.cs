// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFCamera.cs
using Newtonsoft.Json;

public class GLTFCamera
{
    public Orthographic orthographic;
    public Perspective perspective;
    [JsonProperty(Required = Required.Always), JsonConverter(typeof(EnumConverter))] public CameraType type;
    public string name;

    public class Orthographic
    {
        [JsonProperty(Required = Required.Always)] public float xmag;
        [JsonProperty(Required = Required.Always)] public float ymag;
        [JsonProperty(Required = Required.Always)] public float zfar;
        [JsonProperty(Required = Required.Always)] public float znear;
    }

    public class Perspective
    {
        public float? aspectRatio;
        [JsonProperty(Required = Required.Always)] public float yfov;
        public float? zfar;
        [JsonProperty(Required = Required.Always)] public float znear;
    }
}